from __future__ import annotations

import json
import hashlib
import io
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

import yaml
from sentinel_xdr_migration.dependencies import dependency_identity

from sentinel_xdr_migration.workflow import (
    complete_workflow_stage,
    initialize_workflow,
    next_workflow_stage,
    package_workflow_v3_1,
    plan_new_package_release,
    plan_release_notes_refresh,
    plan_same_version_content_rebuild,
    _yolo_package_readiness,
    read_authoring_contract,
    refresh_yolo_authoring,
    recover_conversion_evidence,
    run_yolo_authoring,
    start_workflow_stage,
    workflow_status,
)
from sentinel_xdr_migration.artifacts import (
    artifact_path,
    create_run,
    list_runs,
    migrate_reports,
    using_run,
)
from sentinel_xdr_migration.budget import (
    BudgetExhausted,
    BudgetReceiptError,
    begin_operation,
    budget_summary,
    extend_budget,
    finish_operation,
)
from sentinel_xdr_migration.converter import convert_solution
from sentinel_xdr_migration.packaging import package_input_file_hashes, package_input_identity
from sentinel_xdr_migration import cli as cli_module
from sentinel_xdr_migration import runtime as runtime_module
from sentinel_xdr_migration.report_dashboard import _run_html
from sentinel_xdr_migration.solution_report import build_solution_report
from test_converter import RULE
from sentinel_xdr_migration import workflow as workflow_module


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.solution = Path(self.temp.name) / "Sample"
        self.solution.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _packaging_artifacts(
        self,
        version_bump: str = "none",
        version: str = "1.0.0",
    ) -> dict[str, str]:
        package = self.solution / "Package"
        package.mkdir(exist_ok=True)
        paths = {
            "mainTemplate": package / "mainTemplate.json",
            "createUiDefinition": package / "createUiDefinition.json",
            "testParameters": package / "testParameters.json",
            "zip": package / f"{version}.zip",
        }
        for path in paths.values():
            path.write_text("{}", encoding="utf-8")
        report = artifact_path(self.solution, "packaging.v3_1.json", create_parent=True)
        report.write_text(
            json.dumps({
                "packager": "V3.1",
                "versionBump": version_bump,
                **{name: str(path) for name, path in paths.items()},
            }),
            encoding="utf-8",
        )
        return {
            "packager": "V3.1",
            "packageReport": str(report),
            **{name: str(path) for name, path in paths.items()},
        }

    def test_package_input_hash_preserves_legacy_path_ordering(self) -> None:
        (self.solution / "Data").mkdir()
        (self.solution / "Data" / "foo").write_bytes(b"data\n")
        (self.solution / "Data Connectors").mkdir()
        (self.solution / "Data Connectors" / "foo").write_bytes(b"connector\n")

        self.assertEqual(
            "a1619ceb3e74e25fecf64a29ebcf9714d89cc13917ce1e63c2b0e091cbd90960",
            package_input_identity(self.solution)["sha256"],
        )

    def _mock_v3_1_package(self, solution: Path, **kwargs: str) -> dict:
        input_before = package_input_identity(solution)
        target_version = kwargs.get("target_version")
        if target_version:
            data_files = sorted((solution / "Data").glob("Solution_*.json"))
            if len(data_files) != 1:
                raise AssertionError("target-version mock requires one solution data file")
            data = json.loads(data_files[0].read_text(encoding="utf-8"))
            data["Version"] = target_version
            data_files[0].write_text(json.dumps(data), encoding="utf-8")
        version = workflow_module.solution_data_version(solution) or "1.0.0"
        artifacts = self._packaging_artifacts(kwargs["version_bump"], version)
        package_hashes = {
            name: hashlib.sha256(Path(artifacts[name]).read_bytes()).hexdigest()
            for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip")
        }
        inputs = package_input_identity(solution)
        input_files = package_input_file_hashes(solution)
        if (
            workflow_module._identity_from_file_hashes(input_files) != inputs["sha256"]
            or len(input_files) != inputs["fileCount"]
        ):
            raise AssertionError("mock V3.1 input manifest does not match its identity")
        attempt_id = kwargs["package_attempt_id"]
        report = {
            "status": "passed",
            "packager": "V3.1",
            "version": version,
            "versionBump": kwargs["version_bump"],
            "requestedVersionBump": kwargs["requested_version_bump"],
            "effectiveVersionBump": kwargs["version_bump"],
            "requestedTargetVersion": target_version,
            "effectiveTargetVersion": target_version,
            "packageAttemptId": attempt_id,
            "workflowRunId": kwargs["workflow_run_id"],
            "packageInputs": {
                "before": input_before,
                "after": {**inputs, "files": input_files},
            },
            "packageArtifactHashes": package_hashes,
            "packageArtifactsSha256": hashlib.sha256(
                json.dumps(package_hashes, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            **{
                name: artifacts[name]
                for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip")
            },
        }
        selection_plan = kwargs.get("selection_plan")
        if selection_plan is not None:
            summary = selection_plan["summary"]
            report.update({
                "selectionOutcome": (
                    "partial-package-validated"
                    if summary["outcome"] == "partial"
                    else "package-validated"
                ),
                "selectionPlanSha256": selection_plan["planSha256"],
                "selectionSummary": summary,
                "selectionVerification": {
                    "planSha256": selection_plan["planSha256"],
                    "outcome": summary["outcome"],
                    "analyticRuleIncluded": summary.get("analyticRuleIncluded"),
                    "xdrDetectionIncluded": summary.get("xdrDetectionIncluded"),
                    "coverageNumerator": summary.get("coverageNumerator"),
                    "coverageDenominator": summary.get("coverageDenominator"),
                    "partialPublicationAllowed": summary.get("partialPublicationAllowed"),
                    "mainTemplateVerified": True,
                    "zipVerified": True,
                },
            })
        report_path = Path(artifacts["packageReport"])
        report_path.write_text(json.dumps(report), encoding="utf-8")
        artifacts["packageReport"] = str(report_path)
        return {
            **report,
            "solution": str(solution),
            "packageReport": str(report_path),
            "workflowArtifacts": {
                "packager": "V3.1",
                "packageReport": str(report_path),
                **{
                    name: artifacts[name]
                    for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip")
                },
            },
        }

    def _mock_v3_1_patch_package(self, solution: Path, **kwargs: str) -> dict:
        before = package_input_identity(solution)
        if kwargs.get("version_bump") != "patch":
            raise AssertionError("patch test helper requires the patch version action")
        data_files = sorted((solution / "Data").glob("Solution_*.json"))
        if len(data_files) != 1:
            raise AssertionError("patch test helper requires one solution data file")
        data = json.loads(data_files[0].read_text(encoding="utf-8"))
        major, minor, patch = (int(part) for part in str(data["Version"]).split("."))
        data["Version"] = f"{major}.{minor}.{patch + 1}"
        data_files[0].write_text(json.dumps(data), encoding="utf-8")
        result = self._mock_v3_1_package(solution, **kwargs)
        report_path = Path(result["packageReport"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["packageInputs"]["before"] = before
        report_path.write_text(json.dumps(report), encoding="utf-8")
        result["packageInputs"]["before"] = before
        return result

    def _prepare_workflow_for_package(self, version_bump: str | None = "patch") -> str:
        self._ensure_solution_release()
        initialized = initialize_workflow(
            self.solution,
            version_bump=version_bump,
            workflow_profile="authoring",
            campaign_id="test-campaign",
        )
        for stage in ("discovery", "conversion", "validation"):
            self._complete_passed_stage(stage)
        return initialized["runId"]

    def _prepare_offline_authoring_validation(
        self,
        *,
        campaign_id: str | None = "test-campaign",
        version_bump: str | None = "none",
    ) -> tuple[dict, Path]:
        self._ensure_solution_release()
        self._create_source_rules()
        initialized = initialize_workflow(
            self.solution,
            version_bump=version_bump,
            workflow_profile="authoring",
            campaign_id=campaign_id,
        )
        with using_run(self.solution, initialized["runId"]):
            start_workflow_stage(self.solution, "discovery")
            complete_workflow_stage(self.solution, "discovery", status="passed")
            start_workflow_stage(self.solution, "conversion")
            conversion = convert_solution(self.solution)
            manifest_path = Path(conversion["manifest"])
            complete_workflow_stage(
                self.solution,
                "conversion",
                status="passed",
                artifacts={
                    "manifest": "manifest.json",
                    "manifestSha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                },
            )
            start_workflow_stage(self.solution, "validation")
        return initialized, manifest_path

    def _qualification_args(self) -> dict[str, str]:
        return {
            "tenant_id": "11111111-2222-4333-8444-555555555555",
            "subscription_id": "22222222-3333-4444-8555-666666666666",
            "workspace_resource_id": (
                "/subscriptions/22222222-3333-4444-8555-666666666666/"
                "resourceGroups/rg/providers/Microsoft.OperationalInsights/"
                "workspaces/ws"
            ),
            "workspace_customer_id": "33333333-4444-4555-8666-777777777777",
        }

    def _complete_passed_stage(self, stage: str) -> None:
        start_workflow_stage(self.solution, stage)
        artifacts = self._packaging_artifacts() if stage == "packaging" else None
        message = None
        if stage == "validation":
            context = workflow_status(self.solution)["context"]
            if context["workflowProfile"] == "authoring":
                artifacts = {"runtimeStatus": "environment-blocked"}
                message = (
                    "Runtime KQL validation was not run; no runtime-qualified "
                    "claim is made."
                )
            else:
                self._create_runtime_evidence()
        complete_workflow_stage(
            self.solution,
            stage,
            status="passed",
            message=message,
            artifacts=artifacts,
        )

    def _create_runtime_evidence(self) -> None:
        source_path = self.solution / "Analytic Rules" / "Rule.yaml"
        output_path = self.solution / "XDR Detections" / "Rule.yaml"
        if not source_path.exists():
            source_path.parent.mkdir(parents=True)
            source_path.write_text(RULE, encoding="utf-8")
        source = yaml.safe_load(source_path.read_text())
        if not output_path.exists():
            output_path.parent.mkdir(parents=True)
            output_path.write_text(yaml.safe_dump({
                "kind": "CustomDetection",
                "contentProvenance": {
                    "source": {"path": "Analytic Rules/Rule.yaml"},
                },
                "properties": {
                    "queryCondition": {
                        "queryText": "DeviceEvents | where Timestamp > ago(1h)",
                    },
                },
            }), encoding="utf-8")
        target = yaml.safe_load(output_path.read_text())
        for provider, query in (
            ("triage-mcp", source["query"]),
            ("graph", target["properties"]["queryCondition"]["queryText"]),
        ):
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            artifact_path(
                self.solution,
                f"runtime-validation.{provider}.json",
                create_parent=True,
            ).write_text(json.dumps({
                "provider": provider,
                "platform": (
                    "Microsoft Sentinel Triage MCP"
                    if provider == "triage-mcp"
                    else "Microsoft Defender XDR Advanced Hunting"
                ),
                "results": [{
                    "detection": "Rule.yaml",
                    "status": "passed",
                    "rowCount": 0,
                    "querySha256": query_hash,
                    **({"dependencyProvenanceSha256": dependency_identity(target)}
                       if provider == "triage-mcp" else {}),
                }],
            }), encoding="utf-8")

    def _ensure_solution_release(self) -> None:
        data = self.solution / "Data/Solution_Sample.json"
        if not data.exists():
            data.parent.mkdir(exist_ok=True)
            data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")

    def _create_source_rules(self, count: int = 1) -> list[Path]:
        paths = []
        for index in range(count):
            path = self.solution / "Analytic Rules" / "Nested" / f"Rule{index}.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)
            document = yaml.safe_load(RULE)
            document["id"] = f"11111111-1111-1111-1111-{index + 1:012d}"
            document["name"] = f"Rule {index}"
            path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            paths.append(path)
        return paths

    def _run_yolo(self, profile: str = "authoring", count: int = 1) -> tuple[dict, dict]:
        self._create_source_rules(count)
        initialized = initialize_workflow(
            self.solution,
            workflow_profile=profile,
            yolo=True,
            campaign_id="test-campaign",
            **(self._qualification_args() if profile == "qualification" else {}),
        )
        with using_run(self.solution, initialized["runId"]):
            result = run_yolo_authoring(self.solution)
            contract = read_authoring_contract(self.solution)
        return result, contract

    def _runtime_reports(self, contract: dict, *, failed_graph_rules: set[str] | None = None) -> None:
        failed_graph_rules = failed_graph_rules or set()
        run = self.solution / "Logs" / "sentinel-xdr-migration" / contract["runId"]
        source_rules = {rule["ruleId"]: rule for rule in contract["inventory"]["rules"]}
        outputs = {
            result["ruleId"]: result["target"]
            for result in contract["results"]
            if result.get("target")
        }
        graph = []
        source = []
        for rule_id, target in outputs.items():
            detection = Path(target["path"]).relative_to("XDR Detections").as_posix()
            graph.append({
                "detection": detection,
                "status": "failed" if rule_id in failed_graph_rules else "passed",
                "querySha256": target["querySha256"],
                "error": "Synthetic KQL failure" if rule_id in failed_graph_rules else None,
            })
            source.append({
                "detection": detection,
                "status": "passed",
                "querySha256": source_rules[rule_id]["querySha256"],
                "error": None,
            })
        run.mkdir(parents=True, exist_ok=True)
        (run / "runtime-validation.graph.json").write_text(
            json.dumps({"provider": "graph", "results": graph}),
            encoding="utf-8",
        )
        (run / "runtime-validation.triage-mcp.json").write_text(
            json.dumps({"provider": "triage-mcp", "results": source}),
            encoding="utf-8",
        )

    def test_profile_selection_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "profile selection is required"):
            initialize_workflow(self.solution, workflow_profile=None)
        defaulted = initialize_workflow(self.solution)
        self.assertEqual("authoring", defaulted["context"]["workflowProfile"])
        self.assertTrue(defaulted["context"]["profileSelectionConfirmed"])

    def test_initialize_creates_resumable_state(self) -> None:
        created = initialize_workflow(
            self.solution,
            workspace_resource_id="/subscriptions/test/workspaces/sample",
            version_bump="patch",
            workflow_profile="authoring",
        )
        resumed = initialize_workflow(
            self.solution,
            workspace_resource_id="/subscriptions/test/workspaces/sample",
            version_bump="patch",
            workflow_profile="authoring",
        )

        self.assertFalse(created["resumed"])
        self.assertTrue(resumed["resumed"])
        self.assertEqual(resumed["next"], "discovery")
        self.assertTrue(
            artifact_path(self.solution, "workflow-state.json").is_file()
        )
        self.assertEqual(
            resumed["stages"]["mockIngestion"]["status"],
            "notRequired",
        )
        self.assertTrue(resumed["context"]["profileSelectionConfirmed"])

    def test_authoring_can_record_tenant_without_qualification_target(self) -> None:
        tenant_id = "11111111-1111-4111-8111-111111111111"
        created = initialize_workflow(
            self.solution,
            tenant_id=tenant_id,
            workflow_profile="authoring",
        )

        context = created["context"]
        self.assertEqual(tenant_id, context["tenantId"])
        self.assertIsNone(context.get("subscriptionId"))
        self.assertIsNone(context.get("workspaceResourceId"))
        self.assertIsNone(context.get("workspaceCustomerId"))
        self.assertFalse(context["targetContextLocked"])

    def test_stage_gate_requires_dependencies(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")

        with self.assertRaisesRegex(ValueError, "blocked by: discovery"):
            start_workflow_stage(self.solution, "conversion")

    def test_legacy_state_is_read_only_until_explicit_copy(self) -> None:
        created = initialize_workflow(self.solution, workflow_profile="authoring")
        preferred = Path(created["statePath"])
        legacy = self.solution / "XDR Detections" / "workflow-state.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        preferred.replace(legacy)

        with self.assertWarnsRegex(UserWarning, "reading legacy"):
            resumed = workflow_status(self.solution)
        self.assertEqual(legacy, Path(resumed["statePath"]))
        self.assertFalse(preferred.is_file())
        with self.assertRaisesRegex(ValueError, "migrate-reports"):
            start_workflow_stage(self.solution, "discovery")
        migrate_reports(self.solution, apply=True)
        self.assertTrue(preferred.is_file())
        self.assertTrue(legacy.exists())
        start_workflow_stage(self.solution, "discovery")
        self.assertEqual("running", workflow_status(self.solution)["stages"]["discovery"]["status"])

    def test_failed_stage_can_be_retried(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        start_workflow_stage(self.solution, "discovery")
        complete_workflow_stage(
            self.solution,
            "discovery",
            status="failed",
            message="source metadata is incomplete",
        )

        retry = start_workflow_stage(self.solution, "discovery")

        self.assertEqual(retry["attempts"], 2)
        self.assertEqual(retry["status"], "running")

    def test_complete_stage_persists_contract_and_unlocks_next(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        start_workflow_stage(self.solution, "discovery")
        result = complete_workflow_stage(
            self.solution,
            "discovery",
            status="passed",
            message="one source rule discovered",
            artifacts={"inspection": "Reports/Sample/sentinel-xdr-migration/inspection.json"},
            evidence=["Analytic Rules/Sample.yaml"],
        )

        self.assertEqual(result["next"], "conversion")
        self.assertEqual(next_workflow_stage(self.solution)["next"], "conversion")
        persisted = workflow_status(self.solution)
        discovery = persisted["stages"]["discovery"]
        self.assertEqual(
            discovery["artifacts"]["inspection"],
            artifact_path(self.solution, "inspection.json").relative_to(self.solution).as_posix(),
        )
        self.assertEqual(discovery["evidence"], ["Analytic Rules/Sample.yaml"])

    def test_context_mismatch_is_rejected(self) -> None:
        initialize_workflow(
            self.solution,
            version_bump="patch",
            workflow_profile="authoring",
        )

        with self.assertRaisesRegex(ValueError, "workflow already uses"):
            initialize_workflow(
                self.solution,
                version_bump="minor",
                workflow_profile="authoring",
            )

    def test_authoring_profile_moves_from_packaging_to_report(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        for stage in ("discovery", "conversion", "validation", "packaging"):
            self._complete_passed_stage(stage)

        self.assertEqual(next_workflow_stage(self.solution)["next"], "report")

    def test_qualification_profile_requires_internal_test_stages(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        self.assertEqual(initialized["stages"]["mockIngestion"]["status"], "pending")
        for stage in ("discovery", "conversion", "validation", "packaging"):
            self._complete_passed_stage(stage)

        self.assertEqual(next_workflow_stage(self.solution)["next"], "deployment")

    def test_authoring_profile_can_change_to_qualification_before_live_stages(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        for stage in ("discovery", "conversion", "validation", "packaging"):
            self._complete_passed_stage(stage)

        changed = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            **self._qualification_args(),
        )

        self.assertEqual("qualification", changed["context"]["workflowProfile"])
        self.assertEqual("pending", changed["stages"]["deployment"]["status"])
        self.assertEqual("deployment", changed["next"])

    def test_ordinary_authoring_new_runs_remain_unbudgeted_across_inventory_changes(self) -> None:
        first = initialize_workflow(self.solution, workflow_profile="authoring")
        rules = self.solution / "Analytic Rules"
        rules.mkdir()
        (rules / "Rule.yaml").write_text("first inventory", encoding="utf-8")

        second = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            new_run=True,
        )

        self.assertNotIn("budget", first)
        self.assertNotIn("budget", second)
        self.assertFalse(
            (self.solution / "Logs" / "sentinel-xdr-migration-campaigns").exists()
        )
        for run_id in (first["runId"], second["runId"]):
            run_directory = (
                self.solution / "Logs" / "sentinel-xdr-migration" / run_id
            )
            self.assertFalse((run_directory / "campaigns").exists())

    def test_packaging_cannot_pass_without_v3_1_evidence(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        for stage in ("discovery", "conversion", "validation"):
            self._complete_passed_stage(stage)
        start_workflow_stage(self.solution, "packaging")

        with self.assertRaisesRegex(ValueError, "requires packager=V3.1"):
            complete_workflow_stage(
                self.solution,
                "packaging",
                status="passed",
            )

    def test_partial_qualification_progresses_without_fabricating_full_validation(self) -> None:
        self._ensure_solution_release()
        initialized = initialize_workflow(
            self.solution,
            version_bump="patch",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        for stage in ("discovery", "conversion"):
            self._complete_passed_stage(stage)
        start_workflow_stage(self.solution, "validation")
        complete_workflow_stage(
            self.solution,
            "validation",
            status="blocked",
            message="One item failed current runtime validation.",
            artifacts={"runtimeStatus": "blocked"},
        )
        plan = {
            "planSha256": "a" * 64,
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
        }
        selection = {
            "plan": plan,
            "planPath": "Logs/plan.json",
            "receiptPath": "Logs/applied.json",
        }
        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ):
            result = package_workflow_v3_1(
                self.solution,
                requested_version_bump="patch",
            )
            with self.assertRaisesRegex(ValueError, "still match the successful V3.1 package"):
                plan_new_package_release(
                    self.solution,
                    version_bump="patch",
                    expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
                )

            state = workflow_status(self.solution)
            next_stage = next_workflow_stage(self.solution)
            started = start_workflow_stage(self.solution, "deployment")
            complete_workflow_stage(self.solution, "deployment", status="passed")
            start_workflow_stage(self.solution, "mockIngestion")
            complete_workflow_stage(self.solution, "mockIngestion", status="passed")
            start_workflow_stage(self.solution, "alertParity")
            complete_workflow_stage(self.solution, "alertParity", status="passed")
            start_workflow_stage(self.solution, "report")
            complete_workflow_stage(self.solution, "report", status="passed")
            completed_state = workflow_status(self.solution)
        self.assertEqual("partial-package-validated", result["selectionOutcome"])
        self.assertEqual("passed", state["stages"]["packaging"]["status"])
        self.assertEqual("blocked", state["stages"]["validation"]["status"])
        self.assertEqual("inProgress", state["workflowStatus"])
        self.assertEqual("inProgress", result["workflowStatus"])
        self.assertEqual(plan["planSha256"], state["stages"]["packaging"]["artifacts"]["selectionPlanSha256"])
        self.assertEqual("partial-package-validated", state["partialSolution"]["status"])
        self.assertFalse(state["partialSolution"]["fullyRuntimeQualified"])
        self.assertEqual("deployment", next_stage["next"])
        self.assertEqual("running", started["status"])
        self.assertEqual("blocked", completed_state["stages"]["validation"]["status"])
        self.assertEqual("partialCompleted", completed_state["workflowStatus"])
        self.assertEqual("passed", completed_state["stages"]["alertParity"]["status"])

    def test_blocked_validation_cannot_package_without_applied_selection(self) -> None:
        self._ensure_solution_release()
        self._create_source_rules()
        initialize_workflow(self.solution, workflow_profile="authoring")
        for stage in ("discovery", "conversion"):
            self._complete_passed_stage(stage)
        start_workflow_stage(self.solution, "validation")
        complete_workflow_stage(
            self.solution,
            "validation",
            status="blocked",
            message="Runtime evidence is incomplete.",
            artifacts={"runtimeStatus": "blocked"},
        )

        with self.assertRaisesRegex(ValueError, "requires passed validation"):
            package_workflow_v3_1(
                self.solution,
                requested_version_bump="none",
            )

    def test_yolo_readiness_never_uses_partial_selection_exception(self) -> None:
        state = {
            "authoring": {"status": "active"},
            "stages": {"validation": {"status": "blocked"}},
        }
        with self.assertRaisesRegex(ValueError, "existing validation stage to pass"):
            _yolo_package_readiness(
                self.solution,
                self.solution / "workflow-state.json",
                state,
                allow_partial_selection=True,
            )

    def test_old_report_is_not_relabelled_as_v3_1(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        for stage in ("discovery", "conversion", "validation"):
            self._complete_passed_stage(stage)
        start_workflow_stage(self.solution, "packaging")
        artifacts = self._packaging_artifacts()
        report = Path(artifacts["packageReport"])
        document = json.loads(report.read_text())
        document["packager"] = "V4"
        report.write_text(json.dumps(document))
        before = report.read_bytes()
        with self.assertRaisesRegex(ValueError, "does not prove V3.1"):
            complete_workflow_stage(
                self.solution, "packaging", status="passed", artifacts=artifacts
            )
        self.assertEqual(before, report.read_bytes())

    def test_consumed_bump_retries_with_none_and_fresh_v3_1_evidence(self) -> None:
        run_id = self._prepare_workflow_for_package("patch")
        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            first = package_workflow_v3_1(
                self.solution,
                requested_version_bump="patch",
            )
            first_report = json.loads(Path(first["packageReport"]).read_text())
            retry = package_workflow_v3_1(
                self.solution,
                requested_version_bump="none",
            )
            retry_report = json.loads(Path(retry["packageReport"]).read_text())

            self.assertEqual(["patch", "none"], [
                call.kwargs["version_bump"] for call in package.call_args_list
            ])
            self.assertEqual("patch", first_report["effectiveVersionBump"])
            self.assertEqual("none", retry_report["requestedVersionBump"])
            self.assertEqual("none", retry_report["effectiveVersionBump"])
            self.assertNotEqual(
                first_report["packageAttemptId"],
                retry_report["packageAttemptId"],
            )
            state = workflow_status(self.solution)
            self.assertEqual(2, state["stages"]["packaging"]["attempts"])
            self.assertTrue(state["packaging"]["lastConsumedAction"]["bumpConsumed"])
            self.assertEqual("none", state["packaging"]["lastConsumedAction"]["requestedVersionBump"])
            self.assertEqual("passed", state["stages"]["packaging"]["status"])
            self.assertEqual(
                2,
                state["budgetSummary"]["usage"]["packageBuilds"],
            )

    def test_changed_package_inputs_reject_none_and_require_a_new_bump(self) -> None:
        run_id = self._prepare_workflow_for_package("patch")
        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            package_workflow_v3_1(self.solution, requested_version_bump="patch")
            changed_input = self.solution / "XDR Detections" / "Detection.yaml"
            changed_input.parent.mkdir(parents=True, exist_ok=True)
            changed_input.write_text("kind: CustomDetection\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "select an explicit new release action"):
                package_workflow_v3_1(self.solution, requested_version_bump="none")
            package.assert_called_once()

            identity = package_input_identity(self.solution)["sha256"]
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=identity,
            )
            package_workflow_v3_1(self.solution, requested_version_bump="patch")
            self.assertEqual(2, package.call_count)
            state = workflow_status(self.solution)
            self.assertEqual(
                "patch",
                state["packaging"]["lastConsumedAction"]["effectiveVersionBump"],
            )

    def test_initial_none_action_can_plan_first_partial_release(self) -> None:
        self._ensure_solution_release()
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        start_workflow_stage(self.solution, "validation")
        complete_workflow_stage(
            self.solution,
            "validation",
            status="blocked",
            message="An excluded detection failed current validation.",
            artifacts={"runtimeStatus": "blocked"},
        )
        plan = {
            "planSha256": "b" * 64,
            "summary": {
                "outcome": "partial",
                "coveragePolicy": "strictly-greater-than-50-percent-of-original-sentinel-rules",
                "originalSourceRuleCount": 3,
                "originalSourceRuleIds": [
                    "11111111-1111-1111-1111-111111111111",
                    "22222222-2222-2222-2222-222222222222",
                    "33333333-3333-3333-3333-333333333333",
                ],
                "validatedMigratedSourceRuleCount": 2,
                "validatedMigratedSourceRuleIds": [
                    "11111111-1111-1111-1111-111111111111",
                    "22222222-2222-2222-2222-222222222222",
                ],
                "coverageNumerator": 2,
                "coverageDenominator": 3,
                "partialPublicationAllowed": True,
            },
        }
        selection = {
            "plan": plan,
            "planPath": "Logs/plan.json",
            "receiptPath": "Logs/applied.json",
        }
        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            with self.assertRaisesRegex(ValueError, "differs from the workflow's selected action"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            before_plan = workflow_status(self.solution)
            self.assertEqual("none", before_plan["context"]["versionBump"])
            self.assertIsNone((before_plan.get("packaging") or {}).get("pendingReleaseAction"))
            self.assertEqual(0, package.call_count)

            identity = package_input_identity(self.solution)["sha256"]
            self.assertEqual(0, cli_module.main([
                "workflow-plan-package-release",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--version-bump", "patch",
                "--expected-package-input-sha256", identity,
            ]))
            after_plan = workflow_status(self.solution)
            self.assertEqual("none", after_plan["context"]["versionBump"])
            self.assertEqual("patch", after_plan["packaging"]["pendingReleaseAction"]["versionBump"])
            self.assertEqual(identity, after_plan["packaging"]["pendingReleaseAction"]["packageInputSha256"])
            self.assertEqual("packaging", next_workflow_stage(self.solution)["next"])
            self.assertEqual(identity, package_input_identity(self.solution)["sha256"])
            self.assertEqual({}, after_plan["packaging"]["releaseActions"][-1]["historicalEvidence"])

            packaged = package_workflow_v3_1(
                self.solution,
                requested_version_bump="patch",
            )

        final = workflow_status(self.solution)
        self.assertEqual("patch", packaged["effectiveVersionBump"])
        self.assertEqual("none", final["context"]["versionBump"])
        self.assertEqual(identity, final["packaging"]["lastConsumedAction"]["packageInputSha256"])
        self.assertEqual("consumed", final["packaging"]["releaseActions"][-1]["status"])
        self.assertIsNone(final["packaging"]["pendingReleaseAction"])

    def _assert_initial_none_action_can_plan_first_complete_release(
        self,
        rule_count: int,
    ) -> None:
        self._ensure_solution_release()
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        self._create_runtime_evidence()
        self._complete_passed_stage("validation")
        rule_ids = [
            f"00000000-0000-0000-0000-{index:012d}"
            for index in range(1, rule_count + 1)
        ]
        summary = {
            "outcome": "complete",
            "coveragePolicy": "strictly-greater-than-50-percent-of-original-sentinel-rules",
            "originalSourceRuleCount": rule_count,
            "originalSourceRuleIds": rule_ids,
            "validatedMigratedSourceRuleCount": rule_count,
            "validatedMigratedSourceRuleIds": rule_ids,
            "coverageNumerator": rule_count,
            "coverageDenominator": rule_count,
            "partialPublicationAllowed": True,
            "analyticRuleIncluded": rule_count,
            "xdrDetectionIncluded": rule_count,
        }
        plan = {"planSha256": "c" * 64, "summary": summary}
        selection = {
            "plan": plan,
            "planPath": "Logs/plan.json",
            "receiptPath": "Logs/applied.json",
        }

        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            with self.assertRaisesRegex(ValueError, "differs from the workflow's selected action"):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            package.assert_not_called()

            identity = package_input_identity(self.solution)["sha256"]
            self.assertEqual(0, cli_module.main([
                "workflow-plan-package-release",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--version-bump", "patch",
                "--expected-package-input-sha256", identity,
            ]))
            planned = workflow_status(self.solution)
            self.assertEqual("none", planned["context"]["versionBump"])
            self.assertEqual(
                "patch",
                planned["packaging"]["pendingReleaseAction"]["versionBump"],
            )
            self.assertEqual(
                identity,
                planned["packaging"]["pendingReleaseAction"]["packageInputSha256"],
            )
            self.assertEqual("packaging", next_workflow_stage(self.solution)["next"])

            result = package_workflow_v3_1(
                self.solution,
                requested_version_bump="patch",
            )

        final = workflow_status(self.solution)
        self.assertEqual("patch", result["effectiveVersionBump"])
        self.assertEqual("none", final["context"]["versionBump"])
        self.assertEqual("passed", final["stages"]["validation"]["status"])
        self.assertEqual("passed", final["stages"]["packaging"]["status"])
        self.assertEqual("consumed", final["packaging"]["releaseActions"][-1]["status"])

    def test_initial_none_action_plans_first_complete_21_rule_release(self) -> None:
        self._assert_initial_none_action_can_plan_first_complete_release(21)

    def test_initial_none_action_plans_first_complete_15_rule_release(self) -> None:
        self._assert_initial_none_action_can_plan_first_complete_release(15)

    def test_first_release_requires_current_applied_complete_selection_and_exact_hash(self) -> None:
        self._ensure_solution_release()
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        self._create_runtime_evidence()
        self._complete_passed_stage("validation")
        current_hash = package_input_identity(self.solution)["sha256"]

        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=None,
        ):
            with self.assertRaisesRegex(ValueError, "first release planning without a prior"):
                plan_new_package_release(
                    self.solution,
                    version_bump="patch",
                    expected_package_input_sha256=current_hash,
                )

        rule_ids = ["11111111-1111-1111-1111-111111111111"]
        selection = {
            "plan": {
                "planSha256": "d" * 64,
                "summary": {
                    "outcome": "complete",
                    "originalSourceRuleCount": 1,
                    "originalSourceRuleIds": rule_ids,
                    "validatedMigratedSourceRuleCount": 1,
                    "validatedMigratedSourceRuleIds": rule_ids,
                    "coverageNumerator": 1,
                    "coverageDenominator": 1,
                    "partialPublicationAllowed": True,
                },
            },
            "planPath": "Logs/plan.json",
            "receiptPath": "Logs/applied.json",
        }
        state_path = Path(workflow_status(self.solution)["statePath"])
        before = state_path.read_bytes()
        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ):
            with self.assertRaisesRegex(ValueError, "package inputs changed after release action selection"):
                plan_new_package_release(
                    self.solution,
                    version_bump="patch",
                    expected_package_input_sha256="0" * 64,
                )
        self.assertEqual(before, state_path.read_bytes())

    def test_offline_authoring_validation_and_first_patch_release(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        with using_run(self.solution, initialized["runId"]):
            validation = complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            state = workflow_status(self.solution)
            self.assertEqual("passed", validation["status"])
            self.assertEqual("not-run", state["stages"]["validation"]["artifacts"]["runtimeStatus"])
            self.assertEqual("not-run", state["runtimeAssessment"]["runtimeStatus"])
            self.assertFalse(state["runtimeAssessment"]["fullyRuntimeQualified"])
            self.assertEqual("packaging", next_workflow_stage(self.solution)["next"])
            self.assertIn(
                "Passed — offline Authoring; runtime not run",
                _run_html(build_solution_report(self.solution)),
            )

            package_hash = package_input_identity(self.solution)["sha256"]
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_hash,
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                package = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )

        final = workflow_status(self.solution)
        self.assertEqual("patch", package["effectiveVersionBump"])
        self.assertEqual("passed", final["stages"]["packaging"]["status"])
        self.assertEqual("consumed", final["packaging"]["releaseActions"][-1]["status"])
        self.assertEqual("current", final["packageFreshness"]["status"])

    def test_same_release_notes_refresh_rebuilds_only_approved_notes_row(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")
        aligned_header = (
            "| **Version** | **Date Modified (DD-MM-YYYY)** | "
            "**Change History**                                                           |"
        )
        aligned_separator = (
            "|-------------|--------------------------------|"
            "------------------------------------------------------------------------------|"
        )
        notes = self.solution / "ReleaseNotes.md"
        notes.write_text(
            aligned_header + "\n"
            + aligned_separator + "\n"
            + "| 3.1.1 | 01-10-2026 | Previous hybrid package refresh for reviewed detections. |\n"
            + "| 3.1.0 | 01-09-2026 | Added reviewed source-rule mappings. |\n"
            + "| 3.0.9 | 01-08-2026 | Improved detection migration provenance. |\n"
            + "| 3.0.0 | 01-07-2026 | Initial hybrid solution release. |\n",
            encoding="utf-8",
        )
        initialized, _ = self._prepare_offline_authoring_validation()
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            legacy_receipt_input = package_input_identity(self.solution)["sha256"]
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                first = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            self.assertEqual(
                legacy_receipt_input,
                workflow_status(self.solution)["packaging"]["lastSuccessful"]["packageInputSha256"],
            )
            version_before = json.loads(data.read_text(encoding="utf-8"))["Version"]
            base_hash = package_input_identity(self.solution)["sha256"]
            self.assertEqual(0, cli_module.main([
                "workflow-plan-release-notes-refresh",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--release-date", "12-10-2026",
                "--change-history", (
                    "Refreshed the V3.1 hybrid package for three disabled Defender XDR "
                    "Custom Detections with reviewed Host mappings and source-rule provenance."
                ),
                "--expected-package-input-sha256", base_hash,
            ]))
            planned = workflow_status(self.solution)["packaging"]["pendingReleaseAction"]
            expected_row = (
                "| 3.2.2 | 12-10-2026 | Refreshed the V3.1 hybrid package for three disabled "
                "Defender XDR Custom Detections with reviewed Host mappings and source-rule "
                "provenance. |"
            )
            original_notes = notes.read_bytes()
            separator_bytes = aligned_separator.encode("utf-8") + b"\n"
            self.assertIn(separator_bytes, original_notes)
            inserted_notes = original_notes.replace(
                separator_bytes,
                separator_bytes + expected_row.encode("utf-8") + b"\n",
                1,
            )
            notes.write_bytes(inserted_notes)
            self.assertEqual(
                hashlib.sha256(inserted_notes).hexdigest(),
                planned["releaseNotesExpectedSha256"],
            )
            with self.assertRaisesRegex(ValueError, "must be rebuilt with --version-bump none"):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as package:
                refreshed = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            package.assert_called_once()
            self.assertEqual("none", refreshed["effectiveVersionBump"])
            self.assertEqual("3.2.2", version_before)
            self.assertEqual(version_before, json.loads(data.read_text(encoding="utf-8"))["Version"])
            self.assertEqual(first["version"], refreshed["version"])
            self.assertEqual(inserted_notes, notes.read_bytes())
            self.assertNotEqual(
                planned["basePackageInputSha256"],
                planned["packageInputSha256"],
            )
            state = workflow_status(self.solution)
            self.assertEqual("current", state["packageFreshness"]["status"])
            self.assertEqual(
                "consumed",
                state["packaging"]["releaseActions"][-1]["status"],
            )
            consumed_patch_action = state["packaging"]["lastConsumedAction"]["attemptId"]
            start_workflow_stage(self.solution, "report")
            complete_workflow_stage(self.solution, "report", status="passed")
            final = workflow_status(self.solution)
            self.assertEqual("passed", final["stages"]["report"]["status"])
            self.assertEqual("current", final["packageFreshness"]["status"])
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as repeat_package:
                repeated = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            repeat_package.assert_called_once()
            repeated_state = workflow_status(self.solution)
            self.assertEqual("none", repeated["effectiveVersionBump"])
            self.assertEqual(
                planned["packageInputSha256"],
                repeated_state["packaging"]["lastSuccessful"]["packageInputSha256"],
            )
            self.assertNotEqual(
                consumed_patch_action,
                repeated_state["packaging"]["lastConsumedAction"]["attemptId"],
            )
            self.assertEqual("current", repeated_state["packageFreshness"]["status"])
            with self.assertRaisesRegex(ValueError, "already exists for unchanged inputs"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            drift = self.solution / "README.md"
            drift.write_text("non-notes drift\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "explicit new release action"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            release_plan = plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            self.assertEqual("patch", release_plan["versionBump"])

    def test_same_release_notes_refresh_rejects_non_notes_changes_and_wrong_row(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")
        notes = self.solution / "ReleaseNotes.md"
        notes.write_text(
            "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
            "|---|---|---|\n"
            "| 0.9.0 | 01-10-2026 | Prior release |\n",
            encoding="utf-8",
        )
        initialized, _ = self._prepare_offline_authoring_validation()
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            plan_release_notes_refresh(
                self.solution,
                release_date="12-10-2026",
                change_history="Approved description",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            unrelated = self.solution / "README.md"
            unrelated.write_text("unexpected change\n", encoding="utf-8")
            notes.write_text(
                notes.read_text(encoding="utf-8").replace(
                    "|---|---|---|\n",
                    "|---|---|---|\n| 3.2.2 | 12-10-2026 | Different description |\n",
                    1,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "package inventory changed|only the exact planned"):
                package_workflow_v3_1(self.solution, requested_version_bump="none")
            unrelated.unlink()
            with self.assertRaisesRegex(ValueError, "does not match the exact approved refresh"):
                package_workflow_v3_1(self.solution, requested_version_bump="none")

    def test_same_release_notes_refresh_repeat_build_without_campaign(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")
        notes = self.solution / "ReleaseNotes.md"
        notes.write_text(
            "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
            "|---|---|---|\n"
            "| 3.1.1 | 01-10-2026 | Previous release |\n",
            encoding="utf-8",
        )
        initialized, _ = self._prepare_offline_authoring_validation(campaign_id=None)
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            base_hash = package_input_identity(self.solution)["sha256"]
            action = plan_release_notes_refresh(
                self.solution,
                release_date="12-10-2026",
                change_history="Approved same-release note",
                expected_package_input_sha256=base_hash,
            )
            state = workflow_status(self.solution)
            pending = state["packaging"]["pendingReleaseAction"]
            notes.write_text(
                notes.read_text(encoding="utf-8").replace(
                    "|---|---|---|\n",
                    "|---|---|---|\n| 3.2.2 | 12-10-2026 | Approved same-release note |\n",
                    1,
                ),
                encoding="utf-8",
            )
            self.assertEqual(action["packageInputSha256After"], pending["packageInputSha256"])
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                package_workflow_v3_1(self.solution, requested_version_bump="none")
                repeated = package_workflow_v3_1(self.solution, requested_version_bump="none")
            self.assertEqual("none", repeated["effectiveVersionBump"])
            self.assertEqual("current", workflow_status(self.solution)["packageFreshness"]["status"])

    def test_same_version_content_rebuild_archives_inputs_and_builds_without_bumping(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.1"}), encoding="utf-8")
        readme = self.solution / "README.md"
        readme.write_text("approved package content before the first build\n", encoding="utf-8")
        initialized, _ = self._prepare_offline_authoring_validation(version_bump="patch")
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_patch_package,
            ):
                first = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            self.assertEqual("3.2.2", first["version"])
            original_input = readme.read_bytes()
            readme.write_text("explicitly approved non-notes content fix\n", encoding="utf-8")
            approved_input = readme.read_bytes()
            approved_hash = package_input_identity(self.solution)["sha256"]
            prior_zip = Path(first["zip"])
            prior_zip_bytes = prior_zip.read_bytes()
            prior_zip.write_bytes(b"stale prior package")
            with self.assertRaisesRegex(ValueError, "artifact is stale: zip"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=approved_hash,
                )
            prior_zip.write_bytes(prior_zip_bytes)
            planned = plan_same_version_content_rebuild(
                self.solution,
                target_version="3.2.2",
                changed_inputs=["README.md"],
                expected_package_input_sha256=approved_hash,
            )
            state = workflow_status(self.solution)
            action = state["packaging"]["pendingReleaseAction"]
            self.assertEqual("same-version-content-rebuild", action["actionType"])
            self.assertEqual("none", action["versionBump"])
            self.assertEqual("3.2.2", action["targetVersion"])
            self.assertEqual(approved_hash, action["packageInputSha256"])
            self.assertEqual(
                hashlib.sha256(approved_input).hexdigest(),
                action["approvedChangedInputs"]["README.md"],
            )
            archived_root = self.solution / planned["inputBackupRoot"]
            self.assertEqual(approved_input, (archived_root / "README.md").read_bytes())
            for artifact in (
                "packageReport", "mainTemplate", "createUiDefinition", "testParameters", "zip",
            ):
                self.assertIn(artifact, planned["historicalEvidence"])
                self.assertTrue(
                    (self.solution / planned["historicalEvidence"][artifact]).is_file()
                )

            readme.write_bytes(approved_input + b"stale plan drift\n")
            with self.assertRaisesRegex(ValueError, "inputs changed or no longer match"):
                package_workflow_v3_1(self.solution, requested_version_bump="none")
            readme.write_bytes(approved_input)
            backup_readme = archived_root / "README.md"
            backup_readme.write_bytes(original_input)
            with self.assertRaisesRegex(ValueError, "input backup is missing or modified"):
                package_workflow_v3_1(self.solution, requested_version_bump="none")
            backup_readme.write_bytes(approved_input)

            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as package:
                rebuilt = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            package.assert_called_once()
            self.assertEqual("none", rebuilt["effectiveVersionBump"])
            self.assertEqual("3.2.2", rebuilt["version"])
            self.assertEqual("3.2.2", json.loads(data.read_text(encoding="utf-8"))["Version"])
            self.assertEqual(approved_input, readme.read_bytes())
            state = workflow_status(self.solution)
            self.assertEqual("consumed", state["packaging"]["releaseActions"][-1]["status"])
            self.assertEqual("current", state["packageFreshness"]["status"])

            first_rebuild_attempt = state["packaging"]["lastConsumedAction"]["attemptId"]
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as repeat_package:
                repeated = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            repeat_package.assert_called_once()
            self.assertEqual("3.2.2", repeated["version"])
            self.assertNotEqual(
                first_rebuild_attempt,
                workflow_status(self.solution)["packaging"]["lastConsumedAction"]["attemptId"],
            )
            self.assertEqual("current", workflow_status(self.solution)["packageFreshness"]["status"])

    def test_same_version_content_rebuild_retry_and_scope_guards(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.1"}), encoding="utf-8")
        readme = self.solution / "README.md"
        readme.write_text("before\n", encoding="utf-8")
        release_notes = self.solution / "ReleaseNotes.md"
        release_notes.write_text("baseline notes\n", encoding="utf-8")
        initialized, _ = self._prepare_offline_authoring_validation(version_bump="patch")
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_patch_package,
            ):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            readme.write_text("approved correction\n", encoding="utf-8")
            expected_hash = package_input_identity(self.solution)["sha256"]
            with self.assertRaisesRegex(ValueError, "exactly match the current solution version"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.3",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=expected_hash,
                )
            with self.assertRaisesRegex(ValueError, "current input identity"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256="0" * 64,
                )
            with self.assertRaisesRegex(ValueError, "ReleaseNotes"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["ReleaseNotes.md"],
                    expected_package_input_sha256=expected_hash,
                )
            plan_same_version_content_rebuild(
                self.solution,
                target_version="3.2.2",
                changed_inputs=["README.md"],
                expected_package_input_sha256=expected_hash,
            )

            def mutate_notes_after_v31(solution: Path, **kwargs: str) -> dict:
                result = self._mock_v3_1_package(solution, **kwargs)
                release_notes.write_text("unapproved during-build notes edit\n", encoding="utf-8")
                return result

            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=mutate_notes_after_v31,
            ):
                with self.assertRaisesRegex(ValueError, "inputs changed or no longer match"):
                    package_workflow_v3_1(
                        self.solution,
                        requested_version_bump="none",
                    )
            release_notes.write_text("baseline notes\n", encoding="utf-8")

            failed_state = workflow_status(self.solution)
            self.assertEqual(
                expected_hash,
                failed_state["packaging"]["pendingReleaseAction"]["packageInputSha256"],
            )
            self.assertEqual("failed", failed_state["packaging"]["currentAttempt"]["status"])
            self.assertEqual("3.2.2", json.loads(data.read_text(encoding="utf-8"))["Version"])
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                retried = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            self.assertEqual("3.2.2", retried["version"])
            self.assertEqual("consumed", workflow_status(self.solution)["packaging"]["releaseActions"][-1]["status"])

    def test_same_version_rebuild_requires_exact_receipt_to_current_path_diff(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.1"}), encoding="utf-8")
        contents = {
            "README.md": b"before\n",
            "ReleaseNotes.md": b"historical notes\n",
            "Hidden.txt": b"hidden before\n",
            "Unchanged.txt": b"unchanged\n",
            "Removed.txt": b"removed before\n",
        }
        for name, value in contents.items():
            (self.solution / name).write_bytes(value)
        initialized, _ = self._prepare_offline_authoring_validation(version_bump="patch")
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_patch_package,
            ):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")

            (self.solution / "README.md").write_bytes(b"approved\n")
            (self.solution / "ReleaseNotes.md").write_bytes(b"unapproved notes change\n")
            (self.solution / "Hidden.txt").write_bytes(b"hidden after\n")
            (self.solution / "Added.txt").write_bytes(b"added\n")
            (self.solution / "Removed.txt").unlink()
            current_hash = package_input_identity(self.solution)["sha256"]
            with self.assertRaisesRegex(ValueError, "does not permit any ReleaseNotes change"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_hash,
                )

            (self.solution / "ReleaseNotes.md").write_bytes(contents["ReleaseNotes.md"])
            current_hash = package_input_identity(self.solution)["sha256"]
            with self.assertRaisesRegex(ValueError, "scope must exactly match"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_hash,
                )

            (self.solution / "Hidden.txt").write_bytes(contents["Hidden.txt"])
            (self.solution / "Added.txt").unlink()
            (self.solution / "Removed.txt").write_bytes(contents["Removed.txt"])
            current_hash = package_input_identity(self.solution)["sha256"]
            with self.assertRaisesRegex(ValueError, "scope must exactly match"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md", "Unchanged.txt"],
                    expected_package_input_sha256=current_hash,
                )

            planned = plan_same_version_content_rebuild(
                self.solution,
                target_version="3.2.2",
                changed_inputs=["README.md"],
                expected_package_input_sha256=current_hash,
            )
            self.assertEqual(
                {"README.md": hashlib.sha256(b"approved\n").hexdigest()},
                workflow_status(self.solution)["packaging"]["pendingReleaseAction"][
                    "approvedChangedInputs"
                ],
            )
            self.assertEqual("blocked", planned["workflowStatus"])

    def test_same_version_rebuild_reconstructs_receipt_bound_legacy_baseline(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.1"}), encoding="utf-8")
        readme = self.solution / "README.md"
        readme.write_bytes(b"legacy baseline\n")
        initialized, _ = self._prepare_offline_authoring_validation(version_bump="patch")
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )

            def legacy_package(solution: Path, **kwargs: str) -> dict:
                result = self._mock_v3_1_patch_package(solution, **kwargs)
                report_path = Path(result["packageReport"])
                report = json.loads(report_path.read_text(encoding="utf-8"))
                report["packageInputs"]["after"].pop("files")
                report_path.write_text(json.dumps(report), encoding="utf-8")
                return result

            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=legacy_package,
            ):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")

            state = workflow_status(self.solution)
            prior_identity = state["packaging"]["lastSuccessful"]["packageInputSha256"]
            prior_files = package_input_file_hashes(self.solution)
            readme.write_bytes(b"legacy content correction\n")
            current_files = package_input_file_hashes(self.solution)
            current_identity = package_input_identity(self.solution)["sha256"]
            evidence_path = (
                Path("Logs")
                / "same-version-content-rebuild"
                / "legacy-baseline-comparison.json"
            )
            evidence_file = self.solution / evidence_path
            evidence_file.parent.mkdir(parents=True)
            evidence = {
                "priorReceiptIdentity": prior_identity,
                "currentIdentity": current_identity,
                "priorFileCount": len(prior_files),
                "currentFileCount": len(current_files),
                "changedInputs": [{
                    "path": "README.md",
                    "beforeSha256": prior_files["README.md"],
                    "currentSha256": current_files["README.md"],
                }],
            }
            evidence_file.write_text(json.dumps(evidence), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "provide exact receipt-bound"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_identity,
                )
            bad_evidence = dict(evidence)
            bad_evidence["changedInputs"] = []
            (evidence_file.parent / "bad-comparison.json").write_text(
                json.dumps(bad_evidence),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "not bound to the successful receipt"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_identity,
                    legacy_baseline_evidence=(
                        evidence_path.parent / "bad-comparison.json"
                    ).as_posix(),
                )
            planned = plan_same_version_content_rebuild(
                self.solution,
                target_version="3.2.2",
                changed_inputs=["README.md"],
                expected_package_input_sha256=current_identity,
                legacy_baseline_evidence=evidence_path.as_posix(),
            )
            action = workflow_status(self.solution)["packaging"]["pendingReleaseAction"]
            self.assertEqual(
                {
                    "path": evidence_path.as_posix(),
                    "sha256": hashlib.sha256(evidence_file.read_bytes()).hexdigest(),
                },
                action["legacyBaselineEvidence"],
            )
            valid_evidence_bytes = evidence_file.read_bytes()
            evidence_file.write_text("changed after planning", encoding="utf-8")
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as package:
                with self.assertRaisesRegex(ValueError, "evidence changed after the rebuild plan"):
                    package_workflow_v3_1(
                        self.solution,
                        requested_version_bump="none",
                    )
            package.assert_not_called()
            evidence_file.write_bytes(valid_evidence_bytes)
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                rebuilt = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            self.assertEqual("3.2.2", rebuilt["version"])
            self.assertEqual("consumed", workflow_status(self.solution)["packaging"][
                "releaseActions"
            ][-1]["status"])
            receipt = json.loads(
                Path(rebuilt["packageReport"]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                package_input_file_hashes(self.solution),
                receipt["packageInputs"]["after"]["files"],
            )
            self.assertEqual("blocked", planned["workflowStatus"])
            verified = workflow_module.verify_same_version_content_rebuild(self.solution)
            self.assertEqual("verified", verified["status"])
            self.assertTrue(verified["receiptVerified"])
            self.assertFalse(verified["stateChanged"])

    def test_failed_v31_candidate_can_be_repaired_and_retried_at_same_version(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.1"}), encoding="utf-8")
        readme = self.solution / "README.md"
        readme.write_text("candidate input\n", encoding="utf-8")
        initialized, _ = self._prepare_offline_authoring_validation(version_bump="patch")
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )

            def failed_initial_build(solution: Path, **kwargs: str) -> dict:
                value = json.loads(data.read_text(encoding="utf-8"))
                value["Version"] = "3.2.2"
                data.write_text(json.dumps(value), encoding="utf-8")
                artifacts = self._packaging_artifacts("patch", "3.2.2")
                Path(artifacts["packageReport"]).unlink()
                raise RuntimeError("synthetic ARM-TTK failure after candidate generation")

            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=failed_initial_build,
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic ARM-TTK failure"):
                    package_workflow_v3_1(self.solution, requested_version_bump="patch")

            failed_state = workflow_status(self.solution)
            failed_package = failed_state["packaging"]
            self.assertIsNone(failed_package["lastSuccessful"])
            self.assertEqual("failed", failed_package["currentAttempt"]["status"])
            self.assertTrue(failed_package["currentAttempt"]["bumpConsumed"])
            self.assertFalse(failed_package["lastConsumedAction"]["packageSucceeded"])
            failed_files = package_input_file_hashes(self.solution)
            failed_identity = package_input_identity(self.solution)["sha256"]
            snapshot = (
                self.solution
                / "Logs"
                / "sentinel-xdr-migration"
                / initialized["runId"]
                / "failed-v31-3.2.2-artifacts"
            )
            for artifact in (
                "mainTemplate.json",
                "createUiDefinition.json",
                "testParameters.json",
                "3.2.2.zip",
            ):
                source = self.solution / "Package" / artifact
                target = snapshot / "Package" / artifact
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            handoff_path = (
                self.solution
                / "Logs"
                / "sentinel-xdr-migration"
                / initialized["runId"]
                / "packaging-arm-ttk-failure-handoff.json"
            )
            generated = {}
            for relative, artifact in (
                ("Package/mainTemplate.json", "mainTemplate.json"),
                ("Package/createUiDefinition.json", "createUiDefinition.json"),
                ("Package/testParameters.json", "testParameters.json"),
                ("Package/3.2.2.zip", "3.2.2.zip"),
            ):
                candidate = self.solution / relative
                generated[relative] = {
                    "bytes": candidate.stat().st_size,
                    "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
                    "qualification": "generated by failed attempt",
                }
            handoff = {
                "artifactKind": "v3-1-arm-ttk-failure-final-handoff",
                "runId": initialized["runId"],
                "solution": self.solution.name,
                "shellStatus": "completed",
                "cliExitCode": 2,
                "v31ChildExitCode": 1,
                "currentVersion": "3.2.2",
                "bumpConsumed": True,
                "lastConsumedAction": failed_package["lastConsumedAction"],
                "currentPackageInput": {
                    "sha256": failed_identity,
                    "fileCount": len(failed_files),
                },
                "generatedArtifacts": generated,
                "packageReportExists": False,
                "failedArtifactSnapshot": "failed-v31-3.2.2-artifacts",
            }
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")

            readme.write_text("approved repair\n", encoding="utf-8")
            current_files = package_input_file_hashes(self.solution)
            current_identity = package_input_identity(self.solution)["sha256"]
            comparison_path = (
                Path("Logs")
                / "sentinel-xdr-migration"
                / initialized["runId"]
                / "failed-candidate-current-input-comparison.json"
            )
            comparison_file = self.solution / comparison_path
            comparison_file.write_text(
                json.dumps({
                    "priorReceiptIdentity": failed_identity,
                    "currentIdentity": current_identity,
                    "priorFileCount": len(failed_files),
                    "currentFileCount": len(current_files),
                    "changedInputs": [{
                        "path": "README.md",
                        "beforeSha256": failed_files["README.md"],
                        "currentSha256": current_files["README.md"],
                    }],
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "target must exactly match"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.3",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_identity,
                    failed_candidate_evidence=handoff_path.relative_to(self.solution),
                    legacy_baseline_evidence=comparison_path,
                )
            original_handoff = handoff_path.read_bytes()
            handoff_path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be a JSON object"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_identity,
                    failed_candidate_evidence=handoff_path.relative_to(self.solution),
                    legacy_baseline_evidence=comparison_path,
                )
            foreign_handoff = dict(handoff)
            foreign_handoff["runId"] = "foreign-run"
            handoff_path.write_text(json.dumps(foreign_handoff), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "matching consumed, failed V3.1 attempt"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256=current_identity,
                    failed_candidate_evidence=handoff_path.relative_to(self.solution),
                    legacy_baseline_evidence=comparison_path,
                )
            handoff_path.write_bytes(original_handoff)
            planned = plan_same_version_content_rebuild(
                self.solution,
                target_version="3.2.2",
                changed_inputs=["README.md"],
                expected_package_input_sha256=current_identity,
                failed_candidate_evidence=handoff_path.relative_to(self.solution),
                legacy_baseline_evidence=comparison_path,
            )
            planned_state = workflow_status(self.solution)
            action = planned_state["packaging"]["pendingReleaseAction"]
            self.assertEqual("same-version-failed-candidate-rebuild", action["actionType"])
            self.assertEqual(failed_package["currentAttempt"]["attemptId"], action["priorPackageAttemptId"])
            self.assertEqual(failed_identity, action["basePackageInputSha256"])
            self.assertIsNone(action.get("priorPackageReportSha256"))
            self.assertTrue(Path(self.solution / planned["historicalEvidence"]["failedCandidateEvidence"]).is_file())

            original_comparison = comparison_file.read_bytes()
            comparison_file.write_text("stale comparison evidence", encoding="utf-8")
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as stale_evidence_package:
                with self.assertRaisesRegex(ValueError, "changed after the rebuild plan"):
                    package_workflow_v3_1(self.solution, requested_version_bump="none")
            stale_evidence_package.assert_not_called()
            comparison_file.write_bytes(original_comparison)

            readme.write_text("stale after approval\n", encoding="utf-8")
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ) as stale_package:
                with self.assertRaisesRegex(ValueError, "inputs changed or no longer match"):
                    package_workflow_v3_1(self.solution, requested_version_bump="none")
            stale_package.assert_not_called()
            readme.write_text("approved repair\n", encoding="utf-8")

            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=RuntimeError("retry still fails"),
            ):
                with self.assertRaisesRegex(RuntimeError, "retry still fails"):
                    package_workflow_v3_1(self.solution, requested_version_bump="none")
            self.assertEqual("3.2.2", workflow_module.solution_data_version(self.solution))
            self.assertEqual(
                "same-version-failed-candidate-rebuild",
                workflow_status(self.solution)["packaging"]["pendingReleaseAction"]["actionType"],
            )

            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                rebuilt = package_workflow_v3_1(self.solution, requested_version_bump="none")
            self.assertEqual("3.2.2", rebuilt["version"])
            self.assertEqual("3.2.2", workflow_module.solution_data_version(self.solution))
            rebuilt_state = workflow_status(self.solution)
            self.assertIsNone(rebuilt_state["packaging"]["pendingReleaseAction"])
            self.assertTrue(rebuilt_state["packaging"]["lastSuccessful"]["packageSucceeded"])
            verified = workflow_module.verify_same_version_content_rebuild(self.solution)
            self.assertEqual("verified", verified["status"])
            self.assertTrue(verified["receiptVerified"])

    def test_same_version_rebuild_scope_accounts_for_additions_and_deletions(self) -> None:
        baseline = {"keep.txt": "a" * 64, "remove.txt": "b" * 64}
        current = {"keep.txt": "c" * 64, "add.txt": "d" * 64}
        approved = {
            "keep.txt": "c" * 64,
            "remove.txt": None,
            "add.txt": "d" * 64,
        }
        self.assertEqual(
            {"add.txt": "d" * 64, "keep.txt": "c" * 64, "remove.txt": None},
            workflow_module._same_version_rebuild_scope(baseline, current, approved),
        )
        with self.assertRaisesRegex(ValueError, "changed-input scope must exactly match"):
            workflow_module._same_version_rebuild_scope(
                baseline,
                current,
                {"keep.txt": "c" * 64},
            )
        with self.assertRaisesRegex(ValueError, "does not permit any ReleaseNotes"):
            workflow_module._same_version_rebuild_scope(
                {"ReleaseNotes.md": "e" * 64},
                {"ReleaseNotes.md": "f" * 64},
                {"ReleaseNotes.md": "f" * 64},
            )

    def test_same_version_content_rebuild_is_authoring_only_and_version_bound(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "only for Authoring"):
                plan_same_version_content_rebuild(
                    self.solution,
                    target_version="3.2.2",
                    changed_inputs=["README.md"],
                    expected_package_input_sha256="a" * 64,
                )

    def test_same_release_notes_refresh_is_authoring_only_and_does_not_reconsume_patch(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        run_id = initialized["runId"]
        with using_run(self.solution, run_id):
            with self.assertRaisesRegex(ValueError, "only for Authoring"):
                plan_release_notes_refresh(
                    self.solution,
                    release_date="12-10-2026",
                    change_history="Approved release note",
                    expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
                )

    def test_same_release_notes_refresh_requires_fresh_package_receipt(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")
        notes = self.solution / "ReleaseNotes.md"
        notes.write_text(
            "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
            "|---|---|---|\n"
            "| 0.9.0 | 01-10-2026 | Prior release |\n",
            encoding="utf-8",
        )
        initialized, _ = self._prepare_offline_authoring_validation()
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                package = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            Path(package["zip"]).write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "artifact is stale: zip"):
                plan_release_notes_refresh(
                    self.solution,
                    release_date="12-10-2026",
                    change_history="Approved release note",
                    expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
                )

    def test_release_notes_refresh_parses_aligned_header_and_rejects_malformed_history(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")
        notes = self.solution / "ReleaseNotes.md"
        aligned_header = (
            "| **Version** | **Date Modified (DD-MM-YYYY)** | "
            "**Change History**                                                           |"
        )
        aligned_separator = (
            "|-------------|--------------------------------|"
            "------------------------------------------------------------------------------|"
        )
        valid_row = "| 3.1.1 | 01-10-2026 | Existing valid history |"
        malformed_cases = [
            (
                "| **Version** | **Date Modified (DD-MM-YYYY)** | **Wrong History** |",
                aligned_separator,
                valid_row,
                "required three-column table header",
            ),
            (
                "| **Date Modified (DD-MM-YYYY)** | **Version** | **Change History** |",
                aligned_separator,
                valid_row,
                "required three-column table header",
            ),
            (
                "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** | **Extra** |",
                "|---|---|---|---|",
                valid_row,
                "required three-column table header",
            ),
            (
                aligned_header,
                "|---|broken|---|",
                valid_row,
                "table separator is invalid",
            ),
            (
                aligned_header,
                aligned_separator,
                "| 3.1.1 | 32-10-2026 | Invalid date |",
                "invalid DD-MM-YYYY date",
            ),
            (
                aligned_header,
                aligned_separator,
                "| 3.1.x | 01-10-2026 | Invalid version |",
                "invalid semantic version",
            ),
            (
                aligned_header,
                aligned_separator,
                "| 3.1.1 | 01-10-2026 | First |\n| 3.1.1 | 01-09-2026 | Duplicate |",
                "duplicate version",
            ),
            (
                aligned_header,
                aligned_separator,
                "| 3.0.0 | 01-10-2026 | Older first |\n| 3.1.1 | 01-09-2026 | Newer second |",
                "not in descending order",
            ),
        ]
        for header, separator, rows, message in malformed_cases:
            with self.subTest(message=message, header=header):
                notes.write_text(f"{header}\n{separator}\n{rows}\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    workflow_module._release_notes_refresh_proposal(
                        self.solution,
                        release_date="12-10-2026",
                        change_history="Approved release history",
                    )

    def test_offline_authoring_rejects_changed_source_inventory(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        source = self.solution / "Analytic Rules" / "Nested" / "Rule0.yaml"
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
        document["query"] += "\n| where Severity == 'High'\n"
        source.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "stale or unresolved|review or conversion findings"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

    def test_offline_authoring_rejects_missing_converted_query(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        target = self.solution / "XDR Detections" / "Nested" / "Rule0.yaml"
        document = yaml.safe_load(target.read_text(encoding="utf-8"))
        document["properties"]["queryCondition"].pop("queryText")
        target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "no Advanced Hunting query"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

    def test_offline_authoring_rejects_new_unconverted_inventory_item(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        self._create_source_rules(count=2)
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "complete source inventory"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

    def test_offline_authoring_requires_conversion_manifest(self) -> None:
        initialized, manifest = self._prepare_offline_authoring_validation()
        manifest.unlink()
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "manifest"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

    def _remove_conversion_manifest_hash(self, state_path: Path) -> None:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stages"]["conversion"]["artifacts"].pop("manifestSha256", None)
        state_path.write_text(json.dumps(state), encoding="utf-8")

    def test_legacy_conversion_manifest_is_recovered_via_explicit_run_command(self) -> None:
        initialized, manifest = self._prepare_offline_authoring_validation()
        state_path = Path(initialized["statePath"])
        self._remove_conversion_manifest_hash(state_path)

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr), mock.patch.object(
            cli_module,
            "configure_logging",
        ):
            result = cli_module.main([
                "workflow-recover-conversion-evidence",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
            ])

        self.assertEqual(0, result, stderr.getvalue())
        recovered = json.loads(stdout.getvalue())
        self.assertEqual("recovered", recovered["status"])
        self.assertEqual(
            hashlib.sha256(manifest.read_bytes()).hexdigest(),
            recovered["manifestSha256"],
        )
        state = workflow_status(self.solution)
        conversion_artifacts = state["stages"]["conversion"]["artifacts"]
        self.assertEqual(recovered["manifestSha256"], conversion_artifacts["manifestSha256"])
        self.assertEqual(
            "offline-authoring-full-revalidation",
            conversion_artifacts["manifestEvidenceRecovery"],
        )
        self.assertEqual("running", state["stages"]["validation"]["status"])

        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
        self.assertEqual("passed", workflow_status(self.solution)["stages"]["validation"]["status"])

    def test_conversion_evidence_recovery_does_not_replace_a_bound_mismatch(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        state_path = Path(initialized["statePath"])
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stages"]["conversion"]["artifacts"]["manifestSha256"] = "0" * 64
        state_path.write_text(json.dumps(state), encoding="utf-8")
        before = state_path.read_bytes()

        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "will not replace a bound digest"):
                recover_conversion_evidence(self.solution)

        self.assertEqual(before, state_path.read_bytes())

    def test_conversion_evidence_recovery_rejects_scoped_manifest(self) -> None:
        initialized, manifest_path = self._prepare_offline_authoring_validation()
        self._remove_conversion_manifest_hash(Path(initialized["statePath"]))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["scope"]["kind"] = "rule"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        state_path = Path(initialized["statePath"])
        state_before = state_path.read_bytes()

        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "complete source inventory"):
                recover_conversion_evidence(self.solution)

        self.assertEqual(state_before, state_path.read_bytes())

    def test_conversion_evidence_recovery_rejects_missing_manifest(self) -> None:
        initialized, manifest_path = self._prepare_offline_authoring_validation()
        state_path = Path(initialized["statePath"])
        self._remove_conversion_manifest_hash(state_path)
        manifest_path.unlink()
        state_before = state_path.read_bytes()

        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "manifest is missing or unsafe"):
                recover_conversion_evidence(self.solution)

        self.assertEqual(state_before, state_path.read_bytes())

    def test_conversion_evidence_recovery_rejects_inventory_drift(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        self._remove_conversion_manifest_hash(Path(initialized["statePath"]))
        self._create_source_rules(count=2)
        state_path = Path(initialized["statePath"])
        state_before = state_path.read_bytes()

        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "complete source inventory"):
                recover_conversion_evidence(self.solution)

        self.assertEqual(state_before, state_path.read_bytes())

    def test_conversion_evidence_recovery_rejects_source_and_technical_drift(self) -> None:
        initialized, manifest_path = self._prepare_offline_authoring_validation()
        state_path = Path(initialized["statePath"])
        self._remove_conversion_manifest_hash(state_path)
        source = self.solution / "Analytic Rules" / "Nested" / "Rule0.yaml"
        source_doc = yaml.safe_load(source.read_text(encoding="utf-8"))
        source_doc["query"] += "\n| where Severity == 'High'\n"
        source.write_text(yaml.safe_dump(source_doc, sort_keys=False), encoding="utf-8")
        state_before = state_path.read_bytes()

        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "stale or unresolved"):
                recover_conversion_evidence(self.solution)
        self.assertEqual(state_before, state_path.read_bytes())

        source_doc["query"] = yaml.safe_load(RULE)["query"]
        source.write_text(yaml.safe_dump(source_doc, sort_keys=False), encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["results"][0]["errors"] = ["synthetic conversion error"]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "technical"):
                recover_conversion_evidence(self.solution)
        self.assertEqual(state_before, state_path.read_bytes())

    def test_conversion_evidence_recovery_rejects_review_and_structural_drift(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        self._remove_conversion_manifest_hash(Path(initialized["statePath"]))
        target = self.solution / "XDR Detections" / "Nested" / "Rule0.yaml"
        document = yaml.safe_load(target.read_text(encoding="utf-8"))
        document["contentProvenance"]["conversion"]["reviewRequired"] = True
        target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        state_path = Path(initialized["statePath"])
        state_before = state_path.read_bytes()

        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "review or conversion findings"):
                recover_conversion_evidence(self.solution)
        self.assertEqual(state_before, state_path.read_bytes())

        document["contentProvenance"]["conversion"]["reviewRequired"] = False
        document["properties"].pop("status", None)
        target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "structural validation to pass"):
                recover_conversion_evidence(self.solution)
        self.assertEqual(state_before, state_path.read_bytes())

    def test_offline_authoring_rejects_missing_conversion_target(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        (self.solution / "XDR Detections" / "Nested" / "Rule0.yaml").unlink()
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "target is missing|target does not exist"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

    def test_yolo_without_authoring_consent_does_not_dispatch_advanced_hunting(self) -> None:
        with mock.patch.object(
            runtime_module,
            "validate_advanced_hunting",
            side_effect=AssertionError("Advanced Hunting must not dispatch without consent"),
        ) as graph_validation, mock.patch.object(
            runtime_module,
            "validate_sentinel_sdk",
            side_effect=AssertionError("Sentinel validation must not dispatch in offline Authoring"),
        ) as sentinel_validation:
            result, _ = self._run_yolo(profile="authoring")

        self.assertEqual("passed", result["validationStatus"])
        self.assertEqual("not-run", result["runtimeStatus"])
        graph_validation.assert_not_called()
        sentinel_validation.assert_not_called()

    def test_offline_authoring_rejects_unresolved_review_and_structural_failure(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        target = self.solution / "XDR Detections" / "Nested" / "Rule0.yaml"
        document = yaml.safe_load(target.read_text(encoding="utf-8"))
        document["contentProvenance"]["conversion"]["reviewRequired"] = True
        target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "review or conversion findings"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

        document["contentProvenance"]["conversion"]["reviewRequired"] = False
        document["properties"].pop("status", None)
        target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "structural validation to pass"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )

    def test_offline_authoring_does_not_override_runtime_failure_reports(self) -> None:
        initialized, _ = self._prepare_offline_authoring_validation()
        target = self.solution / "XDR Detections" / "Nested" / "Rule0.yaml"
        target_doc = yaml.safe_load(target.read_text(encoding="utf-8"))
        with using_run(self.solution, initialized["runId"]):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            runtime_module._write_runtime_artifacts(
                self.solution,
                "graph",
                [{
                    "detection": "Nested/Rule0.yaml",
                    "status": "failed",
                    "querySha256": hashlib.sha256(
                        target_doc["properties"]["queryCondition"]["queryText"].encode()
                    ).hexdigest(),
                    "error": "Synthetic current KQL failure",
                }],
            )
            state = workflow_status(self.solution)
            self.assertEqual("blocked", state["stages"]["validation"]["status"])
            self.assertIn(
                "new graph provider evidence",
                state["stages"]["validation"]["message"],
            )
            self.assertEqual("blocked", state["runtimeAssessment"]["runtimeStatus"])

    def test_qualification_cannot_use_offline_authoring_validation_mode(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        with using_run(self.solution, initialized["runId"]):
            start_workflow_stage(self.solution, "discovery")
            complete_workflow_stage(self.solution, "discovery", status="passed")
            start_workflow_stage(self.solution, "conversion")
            complete_workflow_stage(self.solution, "conversion", status="passed")
            start_workflow_stage(self.solution, "validation")
            with self.assertRaisesRegex(ValueError, "only for Authoring"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                    artifacts={
                        "runtimeStatus": "not-run",
                        "validationMode": "offline-authoring",
                    },
                )
            with self.assertRaisesRegex(ValueError, "complete Sentinel and Advanced Hunting"):
                complete_workflow_stage(
                    self.solution,
                    "validation",
                    status="passed",
                )

    def test_conversion_evidence_recovery_rejects_qualification(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "restricted to explicitly selected Authoring"):
                recover_conversion_evidence(self.solution)

    def test_consumed_initial_release_cannot_be_replanned_and_retries_with_none(self) -> None:
        data_path = self.solution / "Data" / "Solution_Sample.json"
        data_path.parent.mkdir(parents=True)
        data_path.write_text(
            json.dumps({"Name": "Sample", "Version": "3.2.3"}),
            encoding="utf-8",
        )
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            workflow_profile="qualification",
            **self._qualification_args(),
        )
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        self._create_runtime_evidence()
        self._complete_passed_stage("validation")
        rule_ids = ["11111111-1111-1111-1111-111111111111"]
        selection = {
            "plan": {
                "planSha256": "e" * 64,
                "summary": {
                    "outcome": "complete",
                    "originalSourceRuleCount": 1,
                    "originalSourceRuleIds": rule_ids,
                    "validatedMigratedSourceRuleCount": 1,
                    "validatedMigratedSourceRuleIds": rule_ids,
                    "coverageNumerator": 1,
                    "coverageDenominator": 1,
                    "partialPublicationAllowed": True,
                    "analyticRuleIncluded": 1,
                    "xdrDetectionIncluded": 1,
                },
            },
            "planPath": "Logs/plan.json",
            "receiptPath": "Logs/applied.json",
        }

        def fail_after_consuming_initial_action(solution: Path, **_kwargs: str) -> dict:
            data = json.loads(data_path.read_text(encoding="utf-8"))
            data["Version"] = "3.2.4"
            data_path.write_text(json.dumps(data), encoding="utf-8")
            raise RuntimeError("synthetic first-build failure after version update")

        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ):
            identity = package_input_identity(self.solution)["sha256"]
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=identity,
            )

        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=fail_after_consuming_initial_action,
        ):
            with self.assertRaisesRegex(RuntimeError, "first-build failure"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            consumed = workflow_status(self.solution)["packaging"]["lastConsumedAction"]
            self.assertTrue(consumed["bumpConsumed"])
            self.assertFalse(consumed["packageSucceeded"])

            with self.assertRaisesRegex(ValueError, "initial version action was consumed by a failed build"):
                plan_new_package_release(
                    self.solution,
                    version_bump="patch",
                    expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
                )

        with using_run(self.solution, initialized["runId"]), mock.patch.object(
            workflow_module,
            "verify_applied_package_selection",
            return_value=selection,
        ), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            retry = package_workflow_v3_1(
                self.solution,
                requested_version_bump="none",
            )
            self.assertEqual("none", retry["effectiveVersionBump"])
            package.assert_called_once()

    def test_stale_package_status_is_read_only_and_new_release_preserves_history(self) -> None:
        run_id = self._prepare_workflow_for_package("none")
        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ):
            first = package_workflow_v3_1(self.solution, requested_version_bump="none")
            original_report = Path(first["packageReport"]).read_bytes()
            original_zip = Path(first["zip"]).read_bytes()
            changed_input = self.solution / "XDR Detections" / "Detection.yaml"
            changed_input.parent.mkdir(parents=True, exist_ok=True)
            changed_input.write_text("kind: CustomDetection\n", encoding="utf-8")

            state_path = Path(workflow_status(self.solution)["statePath"])
            state_before = state_path.read_bytes()
            freshness = workflow_status(self.solution)["packageFreshness"]
            self.assertEqual("stale", freshness["status"])
            self.assertEqual(state_before, state_path.read_bytes())
            next_stage = next_workflow_stage(self.solution)
            self.assertEqual("packaging", next_stage["next"])
            self.assertTrue(next_stage["releaseActionRequired"])

            changed_identity = package_input_identity(self.solution)["sha256"]
            with self.assertRaisesRegex(ValueError, "changed after release action selection"):
                plan_new_package_release(
                    self.solution,
                    version_bump="patch",
                    expected_package_input_sha256="0" * 64,
                )
            planned = plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=changed_identity,
            )
            state = workflow_status(self.solution)
            self.assertEqual("blocked", state["stages"]["packaging"]["status"])
            self.assertEqual("blocked", state["stages"]["report"]["status"])
            self.assertEqual("selected", state["packaging"]["releaseActions"][-1]["status"])
            evidence = state["packaging"]["releaseActions"][-1]["historicalEvidence"]
            self.assertEqual(original_report, (self.solution / evidence["packageReport"]).read_bytes())
            self.assertEqual(original_zip, (self.solution / evidence["zip"]).read_bytes())

            rebuilt = package_workflow_v3_1(self.solution, requested_version_bump="patch")
            self.assertEqual("patch", rebuilt["effectiveVersionBump"])
            self.assertIsNone(workflow_status(self.solution)["packaging"]["pendingReleaseAction"])
            self.assertEqual("consumed", workflow_status(self.solution)["packaging"]["releaseActions"][-1]["status"])
            self.assertEqual("current", workflow_status(self.solution)["packageFreshness"]["status"])
            self.assertEqual(changed_identity, planned["packageInputSha256"])

    def test_failed_new_release_consumption_retries_without_second_bump(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir()
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.3"}), encoding="utf-8")
        run_id = self._prepare_workflow_for_package("none")
        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ):
            package_workflow_v3_1(self.solution, requested_version_bump="none")
            changed_input = self.solution / "XDR Detections" / "Detection.yaml"
            changed_input.parent.mkdir(parents=True, exist_ok=True)
            changed_input.write_text(
                "kind: CustomDetection\n", encoding="utf-8"
            )
            plan_new_package_release(
                self.solution,
                version_bump="patch",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )

        def fail_after_consuming_release(solution: Path, **kwargs: str) -> dict:
            document = json.loads(data.read_text(encoding="utf-8"))
            document["Version"] = "3.2.4"
            data.write_text(json.dumps(document), encoding="utf-8")
            raise RuntimeError("synthetic failed release after version update")

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=fail_after_consuming_release,
        ):
            with self.assertRaisesRegex(RuntimeError, "failed release"):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            state = workflow_status(self.solution)
            self.assertIsNone(state["packaging"]["pendingReleaseAction"])
            self.assertEqual("consumed", state["packaging"]["releaseActions"][-1]["status"])
            self.assertFalse(state["packaging"]["lastConsumedAction"]["packageSucceeded"])

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            retry = package_workflow_v3_1(self.solution, requested_version_bump="none")
            self.assertEqual("none", retry["effectiveVersionBump"])
            package.assert_called_once()

    def test_failed_packager_consuming_bump_allows_only_hash_matching_none_retry(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir()
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.3"}), encoding="utf-8")
        run_id = self._prepare_workflow_for_package("patch")

        def fail_after_bumping(solution: Path, **kwargs: str) -> dict:
            document = json.loads(data.read_text(encoding="utf-8"))
            document["Version"] = "3.2.4"
            data.write_text(json.dumps(document), encoding="utf-8")
            raise RuntimeError("synthetic package failure after version update")

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=fail_after_bumping,
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic package failure"):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            state = workflow_status(self.solution)
            self.assertTrue(state["packaging"]["lastConsumedAction"]["bumpConsumed"])
            self.assertFalse(state["packaging"]["lastConsumedAction"]["packageSucceeded"])

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            result = package_workflow_v3_1(self.solution, requested_version_bump="none")
            self.assertEqual("none", result["effectiveVersionBump"])
            package.assert_called_once()

    def test_explicit_target_version_survives_resume_and_rebuilds_without_reapplying(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir()
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.0.7"}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "cannot be combined"):
            initialize_workflow(
                self.solution,
                version_bump="patch",
                target_version="3.2.2",
                workflow_profile="authoring",
            )
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            target_version="3.2.2",
            workflow_profile="authoring",
            campaign_id="target-version-campaign",
        )
        run_id = initialized["runId"]
        for stage in ("discovery", "conversion", "validation"):
            self._complete_passed_stage(stage)

        resumed = initialize_workflow(
            self.solution,
            version_bump="none",
            target_version="3.2.2",
            workflow_profile="authoring",
            campaign_id="target-version-campaign",
        )
        self.assertTrue(resumed["resumed"])
        self.assertEqual("3.2.2", resumed["context"]["targetVersion"])

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            built = package_workflow_v3_1(
                self.solution,
                requested_version_bump="none",
                requested_target_version="3.2.2",
            )
            self.assertEqual("3.2.2", json.loads(data.read_text())["Version"])
            self.assertEqual("3.2.2", built["version"])
            self.assertEqual("3.2.2", workflow_status(self.solution)["packaging"]["lastConsumedAction"]["effectiveTargetVersion"])
            package.assert_called_once()
            self.assertEqual("3.2.2", package.call_args.kwargs["target_version"])

            resumed = initialize_workflow(
                self.solution,
                version_bump="none",
                target_version="3.2.2",
                workflow_profile="authoring",
                campaign_id="target-version-campaign",
            )
            self.assertEqual("3.2.2", resumed["context"]["targetVersion"])
            rebuilt = package_workflow_v3_1(
                self.solution,
                requested_version_bump="none",
            )
            self.assertEqual("3.2.2", rebuilt["version"])
            self.assertIsNone(package.call_args.kwargs["target_version"])
            self.assertEqual("3.2.2", json.loads(data.read_text())["Version"])
            with self.assertRaisesRegex(ValueError, "version action was already consumed"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                    requested_target_version="3.2.3",
                )

    def test_target_release_plan_binds_exact_version_and_current_inputs(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir()
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.2"}), encoding="utf-8")
        run_id = self._prepare_workflow_for_package("none")
        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ):
            package_workflow_v3_1(self.solution, requested_version_bump="none")
            changed_input = self.solution / "XDR Detections" / "Detection.yaml"
            changed_input.parent.mkdir(parents=True, exist_ok=True)
            changed_input.write_text("kind: CustomDetection\n", encoding="utf-8")
            original = changed_input.read_bytes()
            planned = plan_new_package_release(
                self.solution,
                target_version="3.2.3",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            self.assertEqual("3.2.3", planned["targetVersion"])
            self.assertEqual("target-version", workflow_status(self.solution)["packaging"]["pendingReleaseAction"]["actionType"])
            with self.assertRaisesRegex(ValueError, "exactly one version bump or target version"):
                plan_new_package_release(
                    self.solution,
                    version_bump="patch",
                    target_version="3.2.4",
                    expected_package_input_sha256=planned["packageInputSha256"],
                )
            with self.assertRaisesRegex(ValueError, "differs from the explicitly selected"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                    requested_target_version="3.2.4",
                )
            changed_input.write_text("kind: CustomDetection\n# input changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from the explicitly selected"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                    requested_target_version="3.2.3",
                )
            changed_input.write_bytes(original)
            built = package_workflow_v3_1(
                self.solution,
                requested_version_bump="none",
                requested_target_version="3.2.3",
            )
            self.assertEqual("3.2.3", built["version"])
            state = workflow_status(self.solution)["packaging"]
            self.assertEqual("consumed", state["releaseActions"][-1]["status"])
            self.assertEqual("3.2.3", state["releaseActions"][-1]["targetVersion"])

    def test_target_version_remains_compatible_with_campaign_and_notes_refresh(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.0.7"}), encoding="utf-8")
        notes = self.solution / "ReleaseNotes.md"
        separator = "|---------|-------------------------------|----------------|\n"
        notes.write_text(
            "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
            + separator
            + "| 3.1.1 | 01-10-2026 | Prior release. |\n"
            + "| 3.1.0 | 01-09-2026 | Older release. |\n",
            encoding="utf-8",
        )
        initialized, _ = self._prepare_offline_authoring_validation(version_bump=None)
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            target_version="3.2.2",
            workflow_profile="authoring",
            campaign_id="test-campaign",
        )
        run_id = initialized["runId"]
        with using_run(self.solution, run_id):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                },
            )
            plan_new_package_release(
                self.solution,
                target_version="3.2.2",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                first = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                    requested_target_version="3.2.2",
                )
            self.assertEqual("3.2.2", first["version"])
            base_hash = package_input_identity(self.solution)["sha256"]
            refresh = plan_release_notes_refresh(
                self.solution,
                release_date="12-10-2026",
                change_history="Approved target release notes.",
                expected_package_input_sha256=base_hash,
            )
            row = "| 3.2.2 | 12-10-2026 | Approved target release notes. |\n"
            notes.write_text(notes.read_text(encoding="utf-8").replace(
                separator, separator + row, 1
            ), encoding="utf-8")
            self.assertEqual(
                refresh["packageInputSha256After"],
                package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(
                workflow_module,
                "package_solution_v3_1",
                side_effect=self._mock_v3_1_package,
            ):
                refreshed = package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                )
            self.assertEqual(first["version"], refreshed["version"])
            self.assertEqual("3.2.2", json.loads(data.read_text())["Version"])
            state = workflow_status(self.solution)["packaging"]
            self.assertEqual("consumed", state["releaseActions"][-1]["status"])

    def test_failed_target_version_write_retries_with_none_without_second_change(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir()
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.0.7"}), encoding="utf-8")
        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            target_version="3.2.2",
            workflow_profile="authoring",
            campaign_id="target-version-retry-campaign",
        )
        run_id = initialized["runId"]
        for stage in ("discovery", "conversion", "validation"):
            self._complete_passed_stage(stage)

        def fail_after_target_write(solution: Path, **kwargs: str) -> dict:
            data.write_text(
                json.dumps({"Name": "Sample", "Version": kwargs["target_version"]}),
                encoding="utf-8",
            )
            raise RuntimeError("synthetic failure after target version write")

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=fail_after_target_write,
        ):
            with self.assertRaisesRegex(RuntimeError, "after target version write"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                    requested_target_version="3.2.2",
                )
            consumed = workflow_status(self.solution)["packaging"]["lastConsumedAction"]
            self.assertTrue(consumed["bumpConsumed"])
            self.assertTrue(consumed["targetConsumed"])
            self.assertEqual("3.2.2", consumed["effectiveTargetVersion"])
            self.assertFalse(consumed["packageSucceeded"])

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ) as package:
            retry = package_workflow_v3_1(self.solution, requested_version_bump="none")
            self.assertEqual("3.2.2", retry["version"])
            package.assert_called_once()
            self.assertIsNone(package.call_args.kwargs["target_version"])
            self.assertEqual("3.2.2", json.loads(data.read_text())["Version"])

    def test_stale_package_artifact_blocks_next_workflow_stage(self) -> None:
        run_id = self._prepare_workflow_for_package("none")
        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=self._mock_v3_1_package,
        ):
            result = package_workflow_v3_1(self.solution, requested_version_bump="none")
            Path(result["zip"]).write_text("stale package", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "package artifact is stale: zip"):
                start_workflow_stage(self.solution, "report")

    def test_v4_package_report_cannot_pass_current_v3_1_attempt(self) -> None:
        run_id = self._prepare_workflow_for_package("patch")

        def old_v4_report(solution: Path, **kwargs: str) -> dict:
            result = self._mock_v3_1_package(solution, **kwargs)
            report_path = Path(result["packageReport"])
            report = json.loads(report_path.read_text())
            report["packager"] = "V4"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            return result

        with using_run(self.solution, run_id), mock.patch.object(
            workflow_module,
            "package_solution_v3_1",
            side_effect=old_v4_report,
        ):
            with self.assertRaisesRegex(ValueError, "does not prove V3.1"):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="patch",
                )
            state = workflow_status(self.solution)
            self.assertEqual("failed", state["stages"]["packaging"]["status"])
            self.assertIsNone(state["packaging"]["lastSuccessful"])

    def test_yolo_package_cli_routes_through_workflow_gates(self) -> None:
        self._create_source_rules()
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "package_workflow_v3_1",
            return_value={"packager": "V3.1"},
        ) as workflow_package:
            result = cli_module.main([
                "package-v3-1",
                "--solution", str(self.solution),
                "--toolkit-root", str(self.solution.parent),
                "--run-id", initialized["runId"],
                "--version-bump", "patch",
                "--legacy-baseline-evidence",
                "Logs/same-version-content-rebuild/baseline.json",
            ])

        self.assertEqual(0, result)
        workflow_package.assert_called_once_with(
            str(self.solution),
            requested_version_bump="patch",
            requested_target_version=None,
            toolkit_root=str(self.solution.parent),
            legacy_baseline_evidence=(
                "Logs/same-version-content-rebuild/baseline.json"
            ),
        )

    def test_release_plan_cli_requires_run_and_routes_exact_action_identity(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
        )
        expected_hash = "a" * 64
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "plan_new_package_release",
            return_value={"versionBump": "patch", "packageInputSha256": expected_hash},
        ) as plan:
            result = cli_module.main([
                "workflow-plan-package-release",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--version-bump", "patch",
                "--expected-package-input-sha256", expected_hash,
            ])

        self.assertEqual(0, result)
        plan.assert_called_once_with(
            str(self.solution),
            version_bump="patch",
            target_version=None,
            expected_package_input_sha256=expected_hash,
        )

    def test_target_version_cli_options_route_to_workflow_apis(self) -> None:
        expected_hash = "b" * 64
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "workflow_status",
            return_value={"context": {"workflowProfile": "authoring"}},
        ), mock.patch.object(
            cli_module,
            "package_workflow_v3_1",
            return_value={"packager": "V3.1"},
        ) as workflow_package:
            result = cli_module.main([
                "package-v3-1",
                "--solution", str(self.solution),
                "--version-bump", "none",
                "--target-version", "3.2.2",
            ])
        self.assertEqual(0, result)
        workflow_package.assert_called_once_with(
            str(self.solution),
            requested_version_bump="none",
            requested_target_version="3.2.2",
            toolkit_root=None,
            legacy_baseline_evidence=None,
        )

        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
        )
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "plan_new_package_release",
            return_value={"targetVersion": "3.2.2", "packageInputSha256": expected_hash},
        ) as release_plan:
            result = cli_module.main([
                "workflow-plan-package-release",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--target-version", "3.2.2",
                "--expected-package-input-sha256", expected_hash,
            ])
        self.assertEqual(0, result)
        release_plan.assert_called_once_with(
            str(self.solution),
            version_bump=None,
            target_version="3.2.2",
            expected_package_input_sha256=expected_hash,
        )

    def test_same_version_rebuild_cli_requires_run_and_exact_input_scope(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
        )
        expected_hash = "c" * 64
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "plan_same_version_content_rebuild",
            return_value={"version": "3.2.2", "packageInputSha256": expected_hash},
        ) as plan:
            result = cli_module.main([
                "workflow-plan-same-version-content-rebuild",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--target-version", "3.2.2",
                "--expected-package-input-sha256", expected_hash,
                "--changed-input", "XDR Detections\\Rule.yaml",
                "--changed-input", "Data\\Solution_Sample.json",
                "--legacy-baseline-evidence",
                "Logs\\same-version-content-rebuild\\baseline.json",
                "--failed-candidate-evidence",
                "Logs\\same-version-content-rebuild\\failure-handoff.json",
            ])

        self.assertEqual(0, result)
        plan.assert_called_once_with(
            str(self.solution),
            target_version="3.2.2",
            changed_inputs=[
                "XDR Detections\\Rule.yaml",
                "Data\\Solution_Sample.json",
            ],
            expected_package_input_sha256=expected_hash,
            legacy_baseline_evidence=(
                "Logs\\same-version-content-rebuild\\baseline.json"
            ),
            failed_candidate_evidence=(
                "Logs\\same-version-content-rebuild\\failure-handoff.json"
            ),
        )

    def test_same_version_rebuild_verification_cli_requires_explicit_run(self) -> None:
        initialized = initialize_workflow(self.solution, workflow_profile="authoring")
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "verify_same_version_content_rebuild",
            return_value={"status": "verified", "stateChanged": False},
        ) as verify:
            result = cli_module.main([
                "workflow-verify-same-version-content-rebuild",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--legacy-baseline-evidence", "Logs/baseline.json",
            ])
        self.assertEqual(0, result)
        verify.assert_called_once_with(
            str(self.solution),
            legacy_baseline_evidence="Logs/baseline.json",
        )

    def test_yolo_review_required_rule_blocks_package_without_clearing_it(self) -> None:
        self._create_source_rules()
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        state = workflow_status(self.solution)
        state["stages"]["validation"]["status"] = "passed"
        record = {
            "inventory": {"rules": [{"ruleId": "source-rule"}]},
            "results": [{
                "ruleId": "source-rule",
                "status": "migrated",
                "conversionStatus": "converted",
                "validationStatus": "passed",
                "reviewRequired": True,
                "target": {"structurallyValid": True},
                "findings": [],
            }],
        }
        with mock.patch.object(
            workflow_module,
            "_current_yolo_record",
            return_value=(record, b""),
        ):
            with self.assertRaisesRegex(ValueError, "explicit-review"):
                _yolo_package_readiness(
                    self.solution,
                    Path(initialized["statePath"]),
                    state,
                )
        self.assertTrue(record["results"][0]["reviewRequired"])

        detection_path = self.solution / "XDR Detections" / "Pending.yaml"
        detection_path.parent.mkdir(parents=True)
        detection_path.write_text(yaml.safe_dump({
            "contentProvenance": {
                "conversion": {
                    "status": "converted",
                    "reviewRequired": True,
                },
            },
        }), encoding="utf-8")
        state.pop("authoring")
        with self.assertRaisesRegex(ValueError, "unresolved detection review flags"):
            _yolo_package_readiness(
                self.solution,
                Path(initialized["statePath"]),
                state,
            )

    def test_yolo_best_effort_entity_mapping_remains_reviewed_but_runtime_testable(self) -> None:
        source_path = self._create_source_rules()[0]
        source = yaml.safe_load(source_path.read_text())
        source["query"] = (
            "DeviceEvents | where TimeGenerated > ago(1h) "
            "| project TimeGenerated, DeviceName, IPAddress"
        )
        source["entityMappings"] = [
            {
                "entityType": "Host",
                "fieldMappings": [
                    {"identifier": "FullName", "columnName": "DeviceName"},
                ],
            },
            {
                "entityType": "IP",
                "fieldMappings": [
                    {"identifier": "Address", "columnName": "IPAddress"},
                ],
            },
        ]
        source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        with using_run(self.solution, initialized["runId"]):
            run_yolo_authoring(self.solution)
            contract = read_authoring_contract(self.solution)

        result = contract["results"][0]
        self.assertEqual(result["status"], "migrated")
        self.assertEqual(result["conversionStatus"], "converted")
        self.assertEqual(result["validationStatus"], "passed")
        self.assertTrue(result["reviewRequired"])
        self.assertTrue(result["mappingAssumptions"])
        self.assertTrue(any(
            finding["findingId"].startswith("review-pending-")
            for finding in result["findings"]
        ))
        runtime_status, _, _ = workflow_module._current_runtime_status(
            self.solution, "authoring", contract
        )
        self.assertEqual(runtime_status, "not-run")

    def test_blocked_stage_requires_explanation(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        start_workflow_stage(self.solution, "discovery")

        with self.assertRaisesRegex(ValueError, "require a message"):
            complete_workflow_stage(
                self.solution,
                "discovery",
                status="blocked",
            )

    def test_validation_cannot_pass_without_current_exact_query_evidence(self) -> None:
        initialize_workflow(self.solution, workflow_profile="qualification", **self._qualification_args())
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        self._create_runtime_evidence()
        graph_report = artifact_path(self.solution, "runtime-validation.graph.json")
        report = json.loads(graph_report.read_text())
        report["results"][0]["querySha256"] = "0" * 64
        graph_report.write_text(json.dumps(report))
        start_workflow_stage(self.solution, "validation")

        with self.assertRaisesRegex(ValueError, "every current query"):
            complete_workflow_stage(self.solution, "validation", status="passed")

    def test_environment_blocked_authoring_cannot_hide_current_kql_failure(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        self._create_runtime_evidence()
        source_report = artifact_path(self.solution, "runtime-validation.triage-mcp.json")
        report = json.loads(source_report.read_text())
        report["results"][0]["status"] = "failed"
        report["results"][0]["error"] = "Failed to resolve table"
        source_report.write_text(json.dumps(report))
        start_workflow_stage(self.solution, "validation")

        with self.assertRaisesRegex(ValueError, "cannot be relabeled environment-blocked"):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                message="environment unavailable",
                artifacts={"runtimeStatus": "environment-blocked"},
            )

    def test_lookback_rewrite_invalidates_completed_runtime_and_downstream_stages(self) -> None:
        initialize_workflow(self.solution, workflow_profile="qualification", **self._qualification_args())
        source_path = self.solution / "Analytic Rules" / "Rule.yaml"
        source_path.parent.mkdir()
        source = yaml.safe_load(RULE)
        source["queryPeriod"] = "4h"
        source["query"] = (
            "DeviceEvents | summarize Count=count() "
            "by TimeGenerated, AccountUpn, IPAddress"
        )
        source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        self._complete_passed_stage("discovery")
        self._complete_passed_stage("conversion")
        self._create_runtime_evidence()
        self._complete_passed_stage("validation")
        self._complete_passed_stage("packaging")

        source = yaml.safe_load(source_path.read_text())
        source["queryPeriod"] = "2h"
        source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
        converted = convert_solution(self.solution, overwrite=True)
        self.assertEqual(1, converted["converted"])
        target_query = yaml.safe_load(
            (self.solution / "XDR Detections/Rule.yaml").read_text()
        )["properties"]["queryCondition"]["queryText"]
        self.assertIn("Timestamp >= ago(2h)", target_query)

        stages = workflow_status(self.solution)["stages"]
        self.assertEqual("blocked", stages["validation"]["status"])
        self.assertIn("previous runtime evidence is historical", stages["validation"]["message"])
        self.assertEqual("blocked", stages["packaging"]["status"])
        report = build_solution_report(self.solution)
        runtime = report["rules"][0]["customDetection"]["runtime"]
        self.assertTrue(runtime)
        self.assertEqual("blocked", runtime[0]["status"])
        sentinel_runtime = report["rules"][0]["analyticRule"]["runtime"]
        self.assertEqual("passed", sentinel_runtime[0]["status"])
        self.assertEqual("matches", sentinel_runtime[0]["queryHashStatus"])

    def test_yolo_freezes_complete_nested_inventory_and_keeps_authoring_opt_in(self) -> None:
        paths = self._create_source_rules(2)
        with self.assertRaisesRegex(ValueError, "profile selection is required"):
            initialize_workflow(self.solution, workflow_profile=None, yolo=True)
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        self.assertTrue(initialized["resumed"] is False)
        self.assertEqual(1, initialized["authoring"]["currentContract"]["revision"])
        with using_run(self.solution, initialized["runId"]):
            record = read_authoring_contract(self.solution)
        self.assertEqual(2, record["coverage"]["N"])
        self.assertEqual(
            {path.relative_to(self.solution).as_posix() for path in paths},
            {rule["path"] for rule in record["inventory"]["rules"]},
        )
        self.assertEqual("unprocessed", record["results"][0]["status"])
        self.assertEqual(2, record["coverage"]["untested"])
        self.assertFalse(record["operationEligibility"]["packagingAuthorized"])

    def test_yolo_budget_stop_preserves_coverage_and_cannot_be_cleared_by_extension(self) -> None:
        self._create_source_rules()
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        with using_run(self.solution, initialized["runId"]):
            original_measured_operation = workflow_module.measured_operation

            def fail_conversion_budget(*args, **kwargs):
                if kwargs.get("dimension") == "conversionPass":
                    raise BudgetExhausted("conversion pass ceiling reached")
                return original_measured_operation(*args, **kwargs)

            with mock.patch.object(
                workflow_module,
                "measured_operation",
                side_effect=fail_conversion_budget,
            ), mock.patch.object(workflow_module, "convert_solution") as converter:
                result = run_yolo_authoring(self.solution)
            converter.assert_not_called()
            self.assertEqual("budget-exhausted", result["status"])
            self.assertFalse(result["workPerformed"])
            state = workflow_status(self.solution)
            self.assertEqual("blocked", state["stages"]["conversion"]["status"])
            self.assertEqual("stopped", state["authoring"]["status"])
            self.assertEqual(0, state["authoringSummary"]["coverage"]["E"])
            self.assertEqual(1, state["authoringSummary"]["coverage"]["N"])
            self.assertEqual(
                0,
                budget_summary(self.solution, "test-campaign")["usage"]["conversionPasses"],
            )
            extend_budget(
                self.solution,
                "test-campaign",
                dimension="conversionPasses",
                new_limit=4,
                actor="owner",
                reason="approved budget extension",
                evidence_reference="approval-4",
            )
            self.assertEqual("budget-exhausted", run_yolo_authoring(self.solution)["status"])

    def test_yolo_replacement_run_links_the_persisted_campaign(self) -> None:
        self._create_source_rules()
        original = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        replacement_directory = create_run(self.solution)
        with using_run(self.solution, replacement_directory.name):
            replacement = initialize_workflow(
                self.solution,
                workflow_profile="authoring",
                yolo=True,
                campaign_id="test-campaign",
            )
            state = workflow_status(self.solution)
        self.assertEqual(original["budget"]["inventorySha256"], replacement["budget"]["inventorySha256"])
        self.assertEqual(
            [original["runId"], replacement["runId"]],
            state["budgetSummary"]["linkedRunIds"],
        )
        self.assertEqual(
            state["budgetSummary"]["campaignId"],
            replacement["budget"]["campaignId"],
        )
        operation = begin_operation(
            self.solution,
            "test-campaign",
            inventory_sha256=replacement["budget"]["inventorySha256"],
            run_id=replacement["runId"],
            dimension="conversionPass",
        )
        finish_operation(
            self.solution,
            "test-campaign",
            operation["operationId"],
            status="failed",
            elapsed_seconds=0.25,
        )
        with using_run(self.solution, replacement["runId"]):
            self.assertEqual(
                1,
                workflow_status(self.solution)["budgetSummary"]["usage"]["conversionPasses"],
            )

    def test_yolo_campaign_inventory_conflict_does_not_create_a_partial_run(self) -> None:
        self._create_source_rules()
        initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        before = list_runs(self.solution)
        source = self.solution / "Analytic Rules" / "Nested" / "Rule0.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")

        with self.assertRaisesRegex(BudgetReceiptError, "different frozen source inventory"):
            initialize_workflow(
                self.solution,
                workflow_profile="authoring",
                yolo=True,
                campaign_id="test-campaign",
                new_run=True,
            )

        self.assertEqual(before, list_runs(self.solution))

    def test_qualification_profile_is_explicit_and_retains_locked_target(self) -> None:
        self._create_source_rules()
        with self.assertRaisesRegex(ValueError, "locked target context"):
            initialize_workflow(
                self.solution,
                workflow_profile="qualification",
                yolo=True,
                campaign_id="test-campaign",
            )
        created = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            yolo=True,
            campaign_id="test-campaign",
            **self._qualification_args(),
        )
        self.assertTrue(created["context"]["profileSelectionConfirmed"])
        self.assertTrue(created["context"]["targetContextLocked"])
        self.assertEqual("qualification", created["context"]["workflowProfile"])

    def test_existing_legacy_run_is_not_implicitly_upgraded_to_yolo(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        self.assertNotIn("authoring", workflow_status(self.solution))
        with self.assertRaisesRegex(ValueError, "cannot be enabled on an existing legacy run"):
            initialize_workflow(
                self.solution,
                workflow_profile="authoring",
                yolo=True,
                campaign_id="test-campaign",
            )
        resumed = initialize_workflow(self.solution, workflow_profile="authoring")
        self.assertTrue(resumed["resumed"])
        self.assertNotIn("authoring", resumed)

    def test_changed_frozen_source_inventory_is_rejected_without_overwriting_edits(self) -> None:
        self._create_source_rules()
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        source = self.solution / "Analytic Rules" / "Nested" / "Rule0.yaml"
        edited = source.read_text(encoding="utf-8") + "\n# preserve owner edit\n"
        source.write_text(edited, encoding="utf-8")
        with using_run(self.solution, initialized["runId"]):
            with self.assertRaisesRegex(ValueError, "frozen YOLO source inventory is stale"):
                run_yolo_authoring(self.solution)
        self.assertEqual(edited, source.read_text(encoding="utf-8"))
        self.assertFalse((self.solution / "XDR Detections" / "Nested" / "Rule0.yaml").exists())

    def test_changed_generated_target_is_rejected_and_preserved_on_refresh(self) -> None:
        _, record = self._run_yolo(count=1)
        target = self.solution / record["results"][0]["target"]["path"]
        edited = target.read_text(encoding="utf-8") + "\n# preserve owner edit\n"
        target.write_text(edited, encoding="utf-8")
        with using_run(self.solution, record["runId"]):
            with self.assertRaisesRegex(ValueError, "generated target hash is stale"):
                refresh_yolo_authoring(self.solution)
        self.assertEqual(edited, target.read_text(encoding="utf-8"))

    def test_synthetic_yolo_flow_reuses_existing_converter_validator_and_never_packages(self) -> None:
        result, record = self._run_yolo(count=1)
        self.assertEqual(1, record["coverage"]["N"])
        self.assertEqual(1, record["coverage"]["M"])
        self.assertEqual("migrated", record["results"][0]["status"])
        self.assertEqual("passed", result["validationStatus"])
        self.assertEqual("packaging", result["next"])
        self.assertFalse(result["packageAuthorized"])
        self.assertFalse(result["qualificationAuthorized"])
        self.assertFalse(result["prCreationAuthorized"])
        stages = workflow_status(
            self.solution
        )["stages"]
        self.assertEqual("passed", stages["conversion"]["status"])
        self.assertEqual("passed", stages["validation"]["status"])
        self.assertEqual("pending", stages["packaging"]["status"])

    def test_yolo_stop_is_durable_after_later_results_improve(self) -> None:
        result, record = self._run_yolo(count=3)
        self.assertEqual(3, record["coverage"]["M"])
        self.assertEqual("active", result["status"])
        with using_run(self.solution, record["runId"]):
            self._runtime_reports(
                record,
                failed_graph_rules={
                    record["results"][0]["ruleId"],
                    record["results"][1]["ruleId"],
                },
            )
            stopped = refresh_yolo_authoring(self.solution)
            self.assertEqual("stopped", stopped["status"])
            self.assertEqual((3, 1, 2), (
                stopped["coverage"]["N"],
                stopped["coverage"]["M"],
                stopped["coverage"]["E"],
            ))
            first_state = workflow_status(self.solution)
            self.assertEqual("blocked", first_state["workflowStatus"])
            self.assertIsNone(first_state["next"])
            self._runtime_reports(record)
            improved = refresh_yolo_authoring(self.solution)
            self.assertEqual((3, 3, 0), (
                improved["coverage"]["N"],
                improved["coverage"]["M"],
                improved["coverage"]["E"],
            ))
            self.assertTrue(improved["coverage"]["migrationThresholdMet"])
            self.assertEqual("stopped", improved["status"])
            self.assertEqual("blocked", improved["workflowStatus"])
            self.assertIsNone(improved["next"])
            no_resume = run_yolo_authoring(self.solution)
            self.assertFalse(no_resume["workPerformed"])
            self.assertEqual("stopped", no_resume["status"])

    def test_shared_provider_error_is_recorded_without_inventing_rule_errors(self) -> None:
        result, record = self._run_yolo(count=2)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        (run / "runtime-validation.graph.json").write_text(
            json.dumps({
                "provider": "graph",
                "providerFailure": {"failureKind": "provider", "error": "Graph unavailable"},
                "results": [],
            }),
            encoding="utf-8",
        )
        with using_run(self.solution, record["runId"]):
            refreshed = refresh_yolo_authoring(self.solution)
            stored = read_authoring_contract(self.solution)
        self.assertEqual(1, refreshed["environmentErrorCount"])
        self.assertEqual(0, stored["coverage"]["E"])
        self.assertEqual(2, stored["coverage"]["N"])
        self.assertEqual(1, len(stored["environmentErrors"]))

    def test_yolo_refresh_uses_complete_sdk_source_family(self) -> None:
        _, record = self._run_yolo(count=1)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        self._runtime_reports(record)
        triage_path = run / "runtime-validation.triage-mcp.json"
        sdk_report = json.loads(triage_path.read_text(encoding="utf-8"))
        triage_path.unlink()
        sdk_report.update({
            "provider": "azure-monitor-sdk",
            "platform": "Microsoft Sentinel Log Analytics (Azure Monitor Query SDK)",
            "familyComplete": True,
        })
        (run / "runtime-validation.azure-monitor-sdk.json").write_text(
            json.dumps(sdk_report),
            encoding="utf-8",
        )
        with using_run(self.solution, record["runId"]):
            refreshed = refresh_yolo_authoring(self.solution)
            stored = read_authoring_contract(self.solution)
        self.assertEqual("active", refreshed["status"])
        self.assertEqual(0, refreshed["environmentErrorCount"])
        self.assertEqual("passed", stored["results"][0]["validationStatus"])

    def test_yolo_identityinfo_failure_is_nonblocking_but_not_runtime_passed(self) -> None:
        _, record = self._run_yolo(count=1)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        self._runtime_reports(record)
        triage_path = run / "runtime-validation.triage-mcp.json"
        source_report = json.loads(triage_path.read_text(encoding="utf-8"))
        diagnostic = (
            "'summarize' operator: Failed to resolve table or column "
            "expression named 'IdentityInfo'"
        )
        source_report.update({
            "querySurface": "microsoft-sentinel-triage",
            "familyComplete": True,
        })
        source_report["results"][0].update({
            "status": "failed",
            "statusCode": 400,
            "failureKind": "query",
            "partial": False,
            "error": {
                "code": "BadArgumentError",
                "message": diagnostic,
                "innererror": {
                    "code": "SEM0100",
                    "message": diagnostic,
                },
            },
        })
        raw_before = json.dumps(source_report, sort_keys=True).encode()
        triage_path.write_bytes(raw_before)

        graph_path = run / "runtime-validation.graph.json"
        graph_report = json.loads(graph_path.read_text(encoding="utf-8"))
        graph_report.update({
            "querySurface": "defender-advanced-hunting",
            "familyComplete": True,
        })
        graph_report["results"][0]["schema"] = [
            {"name": "Timestamp", "type": "DateTime"}
        ]
        graph_path.write_text(json.dumps(graph_report), encoding="utf-8")

        with using_run(self.solution, record["runId"]):
            refreshed = refresh_yolo_authoring(self.solution)
            stored = read_authoring_contract(self.solution)
            evidence = workflow_module._current_runtime_status(
                self.solution, "authoring", stored
            )[2]
        result = stored["results"][0]
        self.assertEqual("active", refreshed["status"])
        self.assertEqual("passed", workflow_status(self.solution)["stages"]["validation"]["status"])
        self.assertEqual(
            "not-run",
            workflow_status(self.solution)["stages"]["validation"]["artifacts"]["runtimeStatus"],
        )
        self.assertEqual(
            "source-waived",
            workflow_status(self.solution)["runtimeAssessment"]["runtimeStatus"],
        )
        self.assertFalse(evidence["passed"])
        self.assertEqual("source-waived", evidence["sourceStatus"])
        self.assertTrue(any(
            finding["kind"] == "error"
            and finding["unresolved"] is False
            and "IdentityInfo" in finding["message"]
            for finding in result["findings"]
        ))
        self.assertEqual(raw_before, triage_path.read_bytes())
        self.assertEqual("failed", json.loads(triage_path.read_text())["results"][0]["status"])

    def test_direct_yolo_source_waiver_rejects_changed_target_review_state(self) -> None:
        _, record = self._run_yolo(count=1)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        self._runtime_reports(record)
        triage_path = run / "runtime-validation.triage-mcp.json"
        source_report = json.loads(triage_path.read_text(encoding="utf-8"))
        diagnostic = (
            "'summarize' operator: Failed to resolve table or column "
            "expression named 'IdentityInfo'"
        )
        source_report.update({
            "querySurface": "microsoft-sentinel-triage",
            "familyComplete": True,
        })
        source_report["results"][0].update({
            "status": "failed",
            "statusCode": 400,
            "failureKind": "query",
            "partial": False,
            "error": {
                "code": "BadArgumentError",
                "message": diagnostic,
                "innererror": {"code": "SEM0100", "message": diagnostic},
            },
        })
        triage_path.write_text(json.dumps(source_report), encoding="utf-8")
        graph_path = run / "runtime-validation.graph.json"
        graph_report = json.loads(graph_path.read_text(encoding="utf-8"))
        graph_report.update({
            "querySurface": "defender-advanced-hunting",
            "familyComplete": True,
        })
        graph_report["results"][0]["schema"] = [
            {"name": "Timestamp", "type": "DateTime"}
        ]
        graph_path.write_text(json.dumps(graph_report), encoding="utf-8")

        target = Path(record["results"][0]["target"]["path"])
        target_path = self.solution / target
        target_document = yaml.safe_load(target_path.read_text(encoding="utf-8"))
        target_query = target_document["properties"]["queryCondition"]["queryText"]
        target_document["contentProvenance"]["conversion"].update({
            "reviewRequired": True,
            "errors": ["new current-target conversion error"],
        })
        target_path.write_text(yaml.safe_dump(target_document), encoding="utf-8")
        self.assertEqual(
            target_query,
            yaml.safe_load(target_path.read_text(encoding="utf-8"))[
                "properties"
            ]["queryCondition"]["queryText"],
        )

        with using_run(self.solution, record["runId"]):
            with self.assertRaisesRegex(ValueError, "generated target hash is stale"):
                workflow_module._validate_current_yolo_targets(
                    self.solution,
                    record,
                )

    def test_yolo_sdk_source_family_rejects_stale_query_hash(self) -> None:
        _, record = self._run_yolo(count=1)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        self._runtime_reports(record)
        triage_path = run / "runtime-validation.triage-mcp.json"
        sdk_report = json.loads(triage_path.read_text(encoding="utf-8"))
        triage_path.unlink()
        sdk_report.update({
            "provider": "azure-monitor-sdk",
            "familyComplete": True,
        })
        sdk_report["results"][0]["querySha256"] = "0" * 64
        (run / "runtime-validation.azure-monitor-sdk.json").write_text(
            json.dumps(sdk_report),
            encoding="utf-8",
        )
        with using_run(self.solution, record["runId"]):
            with self.assertRaisesRegex(ValueError, "stale azure-monitor-sdk query hash"):
                refresh_yolo_authoring(self.solution)

    def test_concurrent_refresh_serializes_contract_writers(self) -> None:
        _, record = self._run_yolo(count=1)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        (run / "runtime-validation.graph.json").write_text(
            json.dumps({
                "provider": "graph",
                "providerFailure": {"failureKind": "provider", "error": "Graph unavailable"},
                "results": [],
            }),
            encoding="utf-8",
        )

        def refresh():
            with using_run(self.solution, record["runId"]):
                return refresh_yolo_authoring(self.solution)

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _: refresh(), range(2)))
        self.assertEqual({3}, {item["authoringContract"]["revision"] for item in outcomes})
        snapshots = list((run / "authoring-contracts").glob("*.json"))
        self.assertEqual(3, len(snapshots))

    def test_interrupted_snapshot_commit_recovers_without_losing_stop_or_results(self) -> None:
        _, record = self._run_yolo(count=1)
        run = self.solution / "Logs" / "sentinel-xdr-migration" / record["runId"]
        (run / "runtime-validation.graph.json").write_text(
            json.dumps({
                "provider": "graph",
                "providerFailure": {"failureKind": "provider", "error": "Graph unavailable"},
                "results": [],
            }),
            encoding="utf-8",
        )
        original_write = workflow_module._atomic_write
        writes = 0

        def fail_state_after_snapshot(path: Path, content: bytes):
            nonlocal writes
            writes += 1
            if writes == 2:
                raise OSError("simulated crash before workflow pointer update")
            return original_write(path, content)

        with using_run(self.solution, record["runId"]):
            with mock.patch.object(workflow_module, "_atomic_write", side_effect=fail_state_after_snapshot):
                with self.assertRaisesRegex(OSError, "simulated crash"):
                    refresh_yolo_authoring(self.solution)
            recovered = refresh_yolo_authoring(self.solution)
            self.assertEqual(3, recovered["authoringContract"]["revision"])
            state = workflow_status(self.solution)
            self.assertEqual(recovered["authoringContract"], state["authoring"]["currentContract"])
            self.assertEqual(1, recovered["environmentErrorCount"])

    def test_atomic_state_write_failure_leaves_previous_state_and_no_partial_file(self) -> None:
        self._create_source_rules()
        created = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="test-campaign",
        )
        with using_run(self.solution, created["runId"]):
            state_path = Path(workflow_status(self.solution)["statePath"])
            before = state_path.read_bytes()
            with mock.patch.object(workflow_module.os, "replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    start_workflow_stage(self.solution, "discovery")
            self.assertEqual(before, state_path.read_bytes())
            self.assertEqual([], list(state_path.parent.glob(".workflow-state.json.*.tmp")))

    def test_cli_yolo_is_explicit_and_requires_an_exact_run_id(self) -> None:
        from sentinel_xdr_migration.cli import main

        self._create_source_rules()
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            init_code = main([
                "workflow-init",
                "--solution", str(self.solution),
                "--workflow-profile", "authoring",
                "--yolo",
                "--campaign-id", "test-campaign",
            ])
        self.assertEqual(0, init_code, stderr.getvalue())
        initialized = json.loads(stdout.getvalue())
        self.assertEqual("yolo", initialized["authoring"]["mode"])

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            missing_run_code = main([
                "workflow-yolo",
                "--solution", str(self.solution),
            ])
        self.assertEqual(2, missing_run_code)
        self.assertIn("explicit --run-id", stderr.getvalue())

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            run_code = main([
                "workflow-yolo",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
            ])
        self.assertEqual(0, run_code)
        outcome = json.loads(stdout.getvalue())
        self.assertEqual("active", outcome["status"])
        self.assertEqual(1, outcome["coverage"]["M"])

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr), mock.patch(
            "sentinel_xdr_migration.cli.export_evidence",
            return_value={"exported": True},
        ) as export:
            export_code = main([
                "export-evidence",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--include-authoring-contract",
            ])
        self.assertEqual(0, export_code, stderr.getvalue())
        self.assertTrue(export.call_args.kwargs["authoring_contract"]["inventory"]["complete"])
        self.assertEqual({"exported": True}, json.loads(stdout.getvalue()))

    def test_workflow_status_and_reports_surface_next_step_blocker_recommendations(self) -> None:
        from sentinel_xdr_migration.report import (
            render_runtime_validation_report,
            render_transformation_report,
            summarize_report_blockers,
        )

        source_path = self._create_source_rules()[0]
        source = yaml.safe_load(source_path.read_text())
        source["query"] = (
            "DeviceEvents | where TimeGenerated > ago(1h) "
            "| project TimeGenerated, DeviceName, IPAddress"
        )
        source["entityMappings"] = [
            {
                "entityType": "Host",
                "fieldMappings": [
                    {"identifier": "FullName", "columnName": "DeviceName"},
                ],
            },
            {
                "entityType": "IP",
                "fieldMappings": [
                    {"identifier": "Address", "columnName": "IPAddress"},
                ],
            },
        ]
        source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")

        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="next-step-campaign",
        )
        with using_run(self.solution, initialized["runId"]):
            run_yolo_authoring(self.solution)
            status = workflow_status(self.solution)
            next_stage = next_workflow_stage(self.solution)

        self.assertIn("nextStepRecommendation", status)
        self.assertIn("nextBlockerReview", status)
        self.assertEqual(status["nextStepRecommendation"], status["nextBlockerReview"])
        self.assertEqual(
            status["nextStepRecommendation"]["summary"],
            next_stage["nextStepRecommendation"]["summary"],
        )
        rec = status["nextStepRecommendation"]
        self.assertGreaterEqual(rec["blockerCount"], 1)
        self.assertTrue(rec["topBlockers"])
        self.assertIn("Next migration step: review blocker", rec["summary"])
        self.assertTrue(
            any(b["category"] == "detectionReview" for b in rec["topBlockers"])
        )

        # Verify report.py blocker summary and HTML rendering
        manifest = {
            "solution": str(self.solution),
            "total": 2,
            "converted": 1,
            "needsReview": 1,
            "reviewRequired": 1,
            "conflicts": 1,
            "results": [
                {
                    "ruleId": str(source["id"]),
                    "displayName": source["name"],
                    "status": "needsReview",
                    "reviewRequired": True,
                    "source": "Analytic Rules/Nested/Rule0.yaml",
                    "output": "XDR Detections/Nested/Rule0.yaml",
                    "reviewReasons": ["Multi-entity alert grouping assumption requires review"],
                    "warnings": [],
                    "errors": [],
                },
                {
                    "ruleId": "rule-2",
                    "displayName": "Second Rule",
                    "status": "conflict",
                    "reviewRequired": False,
                    "source": "Analytic Rules/Nested/Rule1.yaml",
                    "output": "XDR Detections/Nested/Rule1.yaml",
                    "reviewReasons": [],
                    "warnings": [],
                    "errors": ["Missing required property"],
                },
            ],
        }
        report_summary = summarize_report_blockers(manifest, kind="transformation")
        self.assertEqual(2, report_summary["blockerCount"])
        self.assertIn("Next migration step: review blockers", report_summary["summary"])
        html = render_transformation_report(manifest)
        self.assertIn("next-step-banner", html)
        self.assertIn("Next migration step: review blockers", html)

        runtime_html = render_runtime_validation_report({
            "solution": str(self.solution),
            "platform": "Microsoft Graph Security Hunting API",
            "provider": "graph",
            "total": 1,
            "valid": 0,
            "invalid": 1,
            "passed": 0,
            "failed": 1,
            "blocked": 0,
            "results": [
                {
                    "detection": "XDR Detections/Nested/Rule0.yaml",
                    "status": "failed",
                    "error": "Semantic error in query",
                }
            ],
        })
        self.assertIn("next-step-banner", runtime_html)
        self.assertIn("Next migration step: review blocker", runtime_html)

    def test_consolidated_review_packet_inventories_detections_and_workbooks_and_cli(self) -> None:
        from sentinel_xdr_migration.workflow import build_consolidated_review_packet

        self._ensure_solution_release()
        source_path = self._create_source_rules()[0]
        source = yaml.safe_load(source_path.read_text())
        source["description"] = "A" * 620 + " truncated description tail."
        source["queryFrequency"] = "5m"
        source["queryPeriod"] = "2d"
        source["query"] = (
            "CustomUnsupportedTable_CL | where TimeGenerated > ago(1h) "
            "| project TimeGenerated, DeviceName, IPAddress"
        )
        source["entityMappings"] = [
            {
                "entityType": "Host",
                "fieldMappings": [
                    {"identifier": "FullName", "columnName": "DeviceName"},
                ],
            },
            {
                "entityType": "IP",
                "fieldMappings": [
                    {"identifier": "Address", "columnName": "IPAddress"},
                ],
            },
        ]
        source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")

        # Add a workbook with an unsupported query table so workbookQueryGaps are populated
        workbooks_dir = self.solution / "Workbooks"
        workbooks_dir.mkdir(parents=True, exist_ok=True)
        (workbooks_dir / "SampleWorkbook.json").write_text(
            json.dumps({
                "version": "Notebook/1.0",
                "items": [
                    {
                        "type": 3,
                        "content": {
                            "version": "KqlItem/1.0",
                            "query": "CustomWorkbookTable_CL | take 10",
                            "size": 0,
                            "queryType": 0,
                            "resourceType": "microsoft.operationalinsights/workspaces",
                        },
                        "name": "query - 0",
                    }
                ],
            }),
            encoding="utf-8",
        )

        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            yolo=True,
            campaign_id="review-packet-campaign",
        )
        # Write a migration-config.yaml with a prior rule override decision inside the run directory
        with using_run(self.solution, initialized["runId"]):
            run_yolo_authoring(self.solution)
            config_path = artifact_path(self.solution, "migration-config.yaml")
            config_path.write_text(
                yaml.safe_dump({
                    "ruleOverrides": {
                        str(source["id"]): {
                            "description": "Reviewed concise description.",
                        }
                    }
                }),
                encoding="utf-8",
            )
            packet = build_consolidated_review_packet(self.solution)

        self.assertEqual("1.0.0", packet["schemaVersion"])
        self.assertEqual("consolidated-review-packet", packet["kind"])
        self.assertEqual(64, len(packet["packetSha256"]))
        self.assertGreaterEqual(packet["summary"]["totalItems"], 1)
        self.assertTrue(packet["categories"]["timing"])
        self.assertTrue(packet["categories"]["entityMappings"])
        self.assertTrue(packet["categories"]["truncatedDescriptions"])
        self.assertTrue(packet["categories"]["dependencyGaps"])
        self.assertTrue(packet["categories"]["workbookQueryGaps"])
        self.assertTrue(packet["groupedFindings"])
        self.assertIn("nextStepRecommendation", packet)
        self.assertIn("Next migration step: review blocker", packet["nextStepRecommendation"]["summary"])

        # Verify preserved prior decision on the truncated description item
        trunc_item = packet["categories"]["truncatedDescriptions"][0]
        self.assertEqual("decided", trunc_item["decisionState"])
        self.assertEqual(
            "Reviewed concise description.",
            trunc_item["priorDecision"]["description"],
        )

        # Verify CLI review-packet and consolidated-review-plan subcommands
        output_file = self.solution / "review-packet-out.json"
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            rc = cli_module.main([
                "review-packet",
                "--solution", str(self.solution),
                "--run-id", initialized["runId"],
                "--output", str(output_file),
            ])
        self.assertEqual(0, rc, stderr.getvalue())
        cli_packet = json.loads(stdout.getvalue())
        self.assertEqual(packet["packetSha256"], cli_packet["packetSha256"])
        self.assertTrue(output_file.is_file())
        written_packet = json.loads(output_file.read_text(encoding="utf-8"))
        self.assertEqual(packet["packetSha256"], written_packet["packetSha256"])

    def test_status_reminder_emits_diagram_batch_explanation_and_suppresses_no_change(self) -> None:
        from sentinel_xdr_migration.workflow import build_migration_status_reminder

        self._ensure_solution_release()
        self._create_source_rules(count=15)
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
        )
        run_id = initialized["runId"]
        with using_run(self.solution, run_id):
            start_workflow_stage(self.solution, "discovery")
            complete_workflow_stage(self.solution, "discovery", status="passed")
            start_workflow_stage(self.solution, "conversion")

            first = build_migration_status_reminder(self.solution, run_id=run_id)
            self.assertFalse(first["suppressedNoChange"])
            self.assertIsNone(first["previousStateFingerprint"])
            self.assertEqual(64, len(first["stateFingerprint"]))
            self.assertIn(
                "Applying reviewed decisions or converting detections before validation",
                first["currentActivity"],
            )
            self.assertIn("[> Conversion <]", first["workflowDiagram"])
            self.assertIn("[Discovery]", first["workflowDiagram"])
            self.assertIsNotNone(first["durationExplanation"])
            self.assertIn("15 source analytic rules", first["durationExplanation"])
            self.assertEqual(
                {
                    "readOnlyObserver": True,
                    "createsExecutor": False,
                    "singleOwnerRespected": True,
                },
                first["watchdogCoordination"],
            )
            self.assertEqual(15, first["itemCounts"]["analyticRules"])

            # Repeat call without state change suppresses repetitive notice
            second = build_migration_status_reminder(self.solution, run_id=run_id)
            self.assertTrue(second["suppressedNoChange"])
            self.assertEqual(first["stateFingerprint"], second["stateFingerprint"])
            self.assertEqual(first["stateFingerprint"], second["previousStateFingerprint"])

            # State change unsuppresses reminder and updates diagram
            complete_workflow_stage(self.solution, "conversion", status="passed")
            start_workflow_stage(self.solution, "validation")
            third = build_migration_status_reminder(self.solution, run_id=run_id)
            self.assertFalse(third["suppressedNoChange"])
            self.assertNotEqual(first["stateFingerprint"], third["stateFingerprint"])
            self.assertEqual(first["stateFingerprint"], third["previousStateFingerprint"])
            self.assertIn("[> Validation <]", third["workflowDiagram"])

        # Verify CLI workflow-status-reminder subcommand
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            rc = cli_module.main([
                "workflow-status-reminder",
                "--solution", str(self.solution),
                "--run-id", run_id,
            ])
        self.assertEqual(0, rc, stderr.getvalue())
        cli_reminder = json.loads(stdout.getvalue())
        self.assertTrue(cli_reminder["suppressedNoChange"])
        self.assertEqual(third["stateFingerprint"], cli_reminder["stateFingerprint"])

    def test_execution_ownership_enforces_single_owner_and_cli(self) -> None:
        from sentinel_xdr_migration.workflow import (
            claim_execution_ownership,
            release_execution_ownership,
        )

        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
        )
        run_id = initialized["runId"]

        claimed = claim_execution_ownership(
            self.solution,
            owner_id="coordinator-alpha",
            operation="convert-and-validate",
            scope={"rules": 7, "workbooks": 1},
            run_id=run_id,
        )
        self.assertEqual("active", claimed["status"])
        self.assertTrue(claimed["singleOwnerEnforced"])
        self.assertEqual("coordinator-alpha", claimed["ownerId"])
        self.assertEqual(0, claimed["renewedCount"])

        # Same owner renewing is permitted
        renewed = claim_execution_ownership(
            self.solution,
            owner_id="coordinator-alpha",
            operation="convert-and-validate",
            scope={"rules": 7, "workbooks": 1},
            run_id=run_id,
        )
        self.assertEqual("active", renewed["status"])
        self.assertEqual(1, renewed["renewedCount"])

        # Conflicting second owner attempting to claim or release the same operation is blocked
        with self.assertRaisesRegex(ValueError, "duplicate_executor_blocked"):
            claim_execution_ownership(
                self.solution,
                owner_id="duplicate-executor-beta",
                operation="convert-and-validate",
                run_id=run_id,
            )
        with self.assertRaisesRegex(ValueError, "duplicate_executor_blocked"):
            release_execution_ownership(
                self.solution,
                owner_id="duplicate-executor-beta",
                operation="convert-and-validate",
                run_id=run_id,
            )

        # Original owner releases lease; another owner can now claim via CLI
        released = release_execution_ownership(
            self.solution,
            owner_id="coordinator-alpha",
            operation="convert-and-validate",
            run_id=run_id,
        )
        self.assertEqual("released", released["status"])
        self.assertIsNotNone(released["releasedAtUtc"])

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            rc = cli_module.main([
                "workflow-execution-owner",
                "--solution", str(self.solution),
                "--run-id", run_id,
                "--action", "claim",
                "--owner-id", "coordinator-beta",
                "--operation", "convert-and-validate",
                "--scope", json.dumps({"rules": 7}),
            ])
        self.assertEqual(0, rc, stderr.getvalue())
        cli_claimed = json.loads(stdout.getvalue())
        self.assertEqual("active", cli_claimed["status"])
        self.assertEqual("coordinator-beta", cli_claimed["ownerId"])

    def test_forward_and_verify_explicit_approval_rejects_tampering_and_wrong_owner(self) -> None:
        from sentinel_xdr_migration.workflow import (
            forward_explicit_approval,
            verify_forwarded_approval,
        )

        initialized = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
        )
        run_id = initialized["runId"]
        exact_scope = {
            "validationMode": "lab-deployment",
            "sentinelRuleCount": 7,
            "workbookCount": 1,
            "customDetectionCount": 7,
            "packageInputSha256": "a" * 64,
        }

        forwarded = forward_explicit_approval(
            self.solution,
            operation="preflight-lab-deployment",
            approved_by="operator-user",
            forwarded_to_owner_id="solution-owner-1",
            exact_scope=exact_scope,
            run_id=run_id,
            reference="chat-turn-42",
        )
        self.assertEqual("active", forwarded["status"])
        approval_sha = forwarded["approvalSha256"]
        self.assertEqual(64, len(approval_sha))

        # Exact match passes verification
        verified = verify_forwarded_approval(
            self.solution,
            owner_id="solution-owner-1",
            operation="preflight-lab-deployment",
            exact_scope=exact_scope,
            approval_sha256=approval_sha,
            run_id=run_id,
        )
        self.assertTrue(verified["verified"])
        self.assertEqual(approval_sha, verified["approvalSha256"])

        # Wrong owner rejected
        with self.assertRaisesRegex(ValueError, "forwarded_approval_owner_mismatch"):
            verify_forwarded_approval(
                self.solution,
                owner_id="wrong-owner-2",
                operation="preflight-lab-deployment",
                exact_scope=exact_scope,
                approval_sha256=approval_sha,
                run_id=run_id,
            )

        # Scope broadening / tampering rejected
        tampered_scope = dict(exact_scope, customDetectionCount=8)
        with self.assertRaisesRegex(ValueError, "forwarded_approval_scope_mismatch"):
            verify_forwarded_approval(
                self.solution,
                owner_id="solution-owner-1",
                operation="preflight-lab-deployment",
                exact_scope=tampered_scope,
                approval_sha256=approval_sha,
                run_id=run_id,
            )

        # Altered hash rejected
        with self.assertRaisesRegex(ValueError, "forwarded_approval_hash_mismatch"):
            verify_forwarded_approval(
                self.solution,
                owner_id="solution-owner-1",
                operation="preflight-lab-deployment",
                exact_scope=exact_scope,
                approval_sha256="f" * 64,
                run_id=run_id,
            )

        # CLI forward + verify round-trip
        cli_scope = {"target": "workbook-review", "count": 1}
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            rc_fwd = cli_module.main([
                "workflow-forward-approval",
                "--solution", str(self.solution),
                "--run-id", run_id,
                "--action", "forward",
                "--operation", "workbook-dependency-apply",
                "--approved-by", "operator-user",
                "--owner-id", "solution-owner-1",
                "--exact-scope", json.dumps(cli_scope),
            ])
        self.assertEqual(0, rc_fwd, stderr.getvalue())
        cli_fwd_payload = json.loads(stdout.getvalue())

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            rc_ver = cli_module.main([
                "workflow-forward-approval",
                "--solution", str(self.solution),
                "--run-id", run_id,
                "--action", "verify",
                "--operation", "workbook-dependency-apply",
                "--owner-id", "solution-owner-1",
                "--exact-scope", json.dumps(cli_scope),
                "--approval-sha256", cli_fwd_payload["approvalSha256"],
            ])
        self.assertEqual(0, rc_ver, stderr.getvalue())
        self.assertTrue(json.loads(stdout.getvalue())["verified"])


if __name__ == "__main__":
    unittest.main()
