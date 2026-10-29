from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from contextlib import nullcontext, redirect_stdout
from io import StringIO
from pathlib import Path, PurePosixPath, PureWindowsPath
from unittest import mock

from sentinel_xdr_migration import arm_acceptance
from sentinel_xdr_migration.arm_acceptance import (
    _BATCH_ARM_ACCEPTANCE_CONFIRMATION,
    _acceptance_package_plan,
    _arm_acceptance_batch_plan,
    _source_paths_in_order,
    execute_arm_template_acceptance_batch,
)
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "arm_template_acceptance_solution"
TARGET = {
    "tenantId": "11111111-2222-3333-4444-555555555555",
    "subscriptionId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "resourceGroup": "arm-acceptance-fixture-rg",
    "workspaceResourceId": (
        "/subscriptions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/"
        "resourceGroups/arm-acceptance-fixture-rg/providers/"
        "Microsoft.OperationalInsights/workspaces/arm-acceptance-fixture-ws"
    ),
    "workspaceCustomerId": "99999999-8888-7777-6666-555555555555",
}
RUN_ID = "synthetic-arm-acceptance-run"
FLAGS = {
    "DeployAnalyticsRule": True,
    "DeployCustomDetection": True,
    "DeployDataConnector": True,
    "DeployPlaybook": True,
    "DeployWorkbook": True,
}
VALIDATION_RECEIPTS = ["current-build-and-validate-report.md"]
MEMBERS = [
    {
        "solution": "FixtureOne",
        "solutionPath": str(FIXTURE_ROOT),
        "runId": RUN_ID,
    }
]
NORMALIZED_MEMBERS = [
    {
        "solution": "FixtureOne",
        "solutionPath": str(FIXTURE_ROOT),
        "runId": RUN_ID,
    }
]


class ArmTemplateAcceptanceTests(unittest.TestCase):
    def test_cli_help_has_only_acceptance_commands_without_full_package_module(self):
        script = """
import builtins
original_import = builtins.__import__
def reject_full_package(name, *args, **kwargs):
    if name.endswith(".full_package"):
        raise AssertionError("acceptance CLI imported the unfinished full-package module")
    return original_import(name, *args, **kwargs)
builtins.__import__ = reject_full_package
from sentinel_xdr_migration.cli import main
try:
    main(["--help"])
except SystemExit as exc:
    if exc.code != 0:
        raise
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("plan-arm-template-acceptance-batch", result.stdout)
        self.assertIn("deploy-arm-template-acceptance-batch", result.stdout)
        self.assertNotIn("plan-full-package-install", result.stdout)
        self.assertNotIn("install-full-package", result.stdout)
        self.assertNotIn("plan-full-package-activation", result.stdout)
        self.assertNotIn("activate-full-package", result.stdout)

    def _package_plan(self, *, flags=FLAGS, template_hash="a" * 64):
        parameters = {
            "workspace": "arm-acceptance-fixture-ws",
            **flags,
        }
        return {
            "status": "ready",
            "stage": "post-validation-arm-template-deployment-acceptance",
            "solution": str(FIXTURE_ROOT),
            "runId": RUN_ID,
            "target": TARGET,
            "packagePlanSha256": "c" * 64,
            "mainTemplatePath": str(FIXTURE_ROOT / "Package" / "mainTemplate.json"),
            "mainTemplateSha256": template_hash,
            "packageIdentity": {
                "version": "3.1.1",
                "packageInputSha256": "d" * 64,
                "packageArtifactHashes": {"mainTemplate": template_hash},
                "packageContentSha256": "9" * 64,
                "packageReportSha256": "8" * 64,
            },
            "mainTemplateSnapshotPath": str(
                FIXTURE_ROOT / "Package" / "acceptance-template-snapshot.json"
            ),
            "mainTemplateSnapshotSha256": template_hash,
            "validationReceipt": {
                "path": VALIDATION_RECEIPTS[0],
                "sha256": "7" * 64,
                "status": "PASSED",
                "validatorSummary": {
                    "total": 3,
                    "passed": 2,
                    "failed": 0,
                    "skipped": 1,
                },
            },
            "declaredContentFlags": flags,
            "parameters": parameters,
            "parametersSha256": arm_acceptance._canonical_sha256(parameters),
        }

    def _batch_plan(self):
        snapshot = FIXTURE_ROOT / "Package" / "acceptance-template-snapshot.json"
        snapshot_hash = arm_acceptance.hashlib.sha256(snapshot.read_bytes()).hexdigest()
        member = self._package_plan(template_hash=snapshot_hash)
        member.update(
            {
                "solution": "FixtureOne",
                "solutionPath": str(FIXTURE_ROOT),
                "deploymentName": "sentinel-arm-fixture-deployment",
            }
        )
        return {
            "status": "ready",
            "stage": "post-validation-arm-template-deployment-acceptance",
            "batchPlanSha256": "b" * 64,
            "target": TARGET,
            "sharedDecisionReceipt": {"sha256": "e" * 64},
            "members": [member],
            "confirmation": _BATCH_ARM_ACCEPTANCE_CONFIRMATION,
        }

    def _state(self):
        return {
            "runId": RUN_ID,
            "context": {
                "workflowProfile": "qualification",
                "profileSelectionConfirmed": True,
                "targetContextLocked": True,
            },
            "stages": {
                "packaging": {
                    "status": "passed",
                    "artifacts": {"packager": "V3.1"},
                },
            },
            "packaging": {
                "lastSuccessful": {
                    "packageReport": "Logs/sentinel-xdr-migration/package-report.json",
                    "packageReportSha256": "8" * 64,
                },
            },
            "packageFreshness": {"status": "current"},
        }

    def _current_package(self, *, template_hash):
        return {
            "status": "current",
            "version": "3.1.1",
            "packageInputSha256": "9" * 64,
            "packageArtifactHashes": {
                "mainTemplate": template_hash,
                "createUiDefinition": "a" * 64,
                "testParameters": "b" * 64,
                "zip": "c" * 64,
            },
            "packageContentSha256": "d" * 64,
            "bicepExtensibilityImports": [{"name": "Microsoft.Security"}],
        }

    def _write_build_validation_receipt(
        self,
        *,
        rows=None,
        summary="Total: 2 validators | 1 passed | 0 failed | 1 skipped",
        result="PASSED",
        source_path_semantics="posix",
        producer_platform=None,
    ):
        toolkit_root = FIXTURE_ROOT / "validation-toolkit"
        if toolkit_root.exists():
            shutil.rmtree(toolkit_root)
        package_report_directory = (
            FIXTURE_ROOT / "Logs" / "sentinel-xdr-migration" / "acceptance-validation-fixture"
        )
        if package_report_directory.exists():
            shutil.rmtree(package_report_directory)
        package_report_directory.mkdir(parents=True)
        package_directory = FIXTURE_ROOT / "Package"
        created_package_files = []
        for name, content in (
            ("createUiDefinition.json", "{\"createUiDefinition\":{}}\n"),
            ("testParameters.json", "{}\n"),
            ("3.1.1.zip", "fixture package archive\n"),
        ):
            path = package_directory / name
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                created_package_files.append(path)

        def file_fingerprints(root, *, excluded=(), path_semantics=None):
            excluded = {name.casefold() for name in excluded}
            rows = []
            paths = list(root.rglob("*"))
            if path_semantics == "windows":
                paths.sort(key=lambda item: PureWindowsPath(item.relative_to(root).as_posix()))
            elif path_semantics == "posix":
                paths.sort(key=lambda item: PurePosixPath(item.relative_to(root).as_posix()))
            else:
                paths.sort(key=lambda item: item.as_posix())
            for path in paths:
                relative = path.relative_to(root)
                if any(part.casefold() in excluded for part in relative.parts):
                    continue
                if any(
                    part.casefold() == ".env" or part.casefold().startswith(".env.")
                    for part in relative.parts
                ):
                    continue
                if path.is_symlink():
                    raise AssertionError(f"fixture unexpectedly contains a symlink: {path}")
                if path.is_file():
                    rows.append(
                        {
                            "path": relative.as_posix(),
                            "sha256": arm_acceptance.hashlib.sha256(path.read_bytes()).hexdigest(),
                        }
                    )
            return rows

        package_artifact_paths = {
            "mainTemplate": "Package/mainTemplate.json",
            "createUiDefinition": "Package/createUiDefinition.json",
            "testParameters": "Package/testParameters.json",
            "zip": "Package/3.1.1.zip",
        }
        package_artifact_hashes = {
            name: arm_acceptance.hashlib.sha256(
                (FIXTURE_ROOT / relative).read_bytes()
            ).hexdigest()
            for name, relative in package_artifact_paths.items()
        }
        package_files = file_fingerprints(package_directory)
        package_report_path = package_report_directory / "packaging.v3_1.json"
        package_input_files = file_fingerprints(
            FIXTURE_ROOT,
            excluded={"package", "logs", "evidence", ".git", ".venv", "__pycache__"},
            path_semantics=source_path_semantics,
        )
        package_input_sha256 = arm_acceptance._canonical_sha256(package_input_files)
        package_artifacts_sha256 = "f" * 64
        package_attempt_id = "attempt-validation-fixture"
        package_workflow_run_id = "run-validation-fixture"
        package_report = {
            "packager": "V3.1",
            "version": "3.1.1",
            "packageAttemptId": package_attempt_id,
            "workflowRunId": package_workflow_run_id,
            "packageInputs": {"after": {"sha256": package_input_sha256}},
            "packageArtifactsSha256": package_artifacts_sha256,
            "packageArtifactHashes": package_artifact_hashes,
            **package_artifact_paths,
        }
        package_report_path.write_text(
            json.dumps(package_report, indent=2) + "\n",
            encoding="utf-8",
        )
        package_identity = {
            "version": "3.1.1",
            "packageInputSha256": package_input_sha256,
            "packageContentSha256": arm_acceptance._canonical_sha256(package_files),
            "packageReportSha256": arm_acceptance.hashlib.sha256(
                package_report_path.read_bytes()
            ).hexdigest(),
            "packageAttemptId": package_attempt_id,
            "workflowRunId": package_workflow_run_id,
            "packageArtifactsSha256": package_artifacts_sha256,
            "recordedPackageArtifactHashes": package_artifact_hashes,
        }

        evidence_path = (
            toolkit_root
            / ".script"
            / "local-validation"
            / "Logs"
            / "20261012T010000000Z"
        )
        evidence_path.mkdir(parents=True, exist_ok=True)
        script_path = (
            toolkit_root
            / ".script"
            / "local-validation"
            / "build-and-validate.ps1"
        )
        script_path.write_text("# test fixture\n", encoding="utf-8")
        binding_script_path = script_path.with_name("validation-binding.ps1")
        binding_script_path.write_text("# binding fixture\n", encoding="utf-8")
        report_path = evidence_path / "build-and-validate-report.md"
        content_root = FIXTURE_ROOT.parent.resolve()
        table = rows if rows is not None else [
            "| TS | TypeScript validators | PASS | 1 passed |",
            "| CI-PS | ARM-TTK | SKIP | no import validation |",
        ]
        binding = {
            "schemaVersion": 1,
            "producer": "build-and-validate.ps1",
            "validationResult": result,
            "validationRan": True,
            "packagingSkipped": True,
            "toolkitRoot": str(toolkit_root.resolve()),
            "contentRoot": str(content_root),
            "solutionPath": str(FIXTURE_ROOT.resolve()),
            "sourcePathSemantics": source_path_semantics,
            "producerPlatform": producer_platform
            or ("windows" if sys.platform == "win32" else "posix"),
            "evidenceRunPath": str(evidence_path.resolve()),
            "validationStartedAtUtc": "2026-10-12T01:00:00+00:00",
            "validationCompletedAtUtc": "2026-10-12T01:01:00+00:00",
            "validatorSummary": {
                "total": len(table),
                "passed": sum("| PASS |" in row for row in table),
                "failed": sum("| FAIL |" in row for row in table),
                "skipped": sum("| SKIP |" in row for row in table),
            },
            "package": {
                "path": package_report_path.relative_to(FIXTURE_ROOT).as_posix(),
                "sha256": package_identity["packageReportSha256"],
                "version": "3.1.1",
                "packageAttemptId": package_attempt_id,
                "workflowRunId": package_workflow_run_id,
                "packageInputSha256": package_input_sha256,
                "packageArtifactsSha256": package_artifacts_sha256,
                "packageArtifactHashes": package_artifact_hashes,
                "packageFiles": package_files,
            },
            "inputFilesBefore": package_input_files,
            "inputFilesAfter": package_input_files,
            "packageFilesBefore": package_files,
            "packageFilesAfter": package_files,
            "producerFilesBefore": {
                "build-and-validate.ps1": arm_acceptance.hashlib.sha256(
                    script_path.read_bytes()
                ).hexdigest(),
                "validation-binding.ps1": arm_acceptance.hashlib.sha256(
                    binding_script_path.read_bytes()
                ).hexdigest(),
            },
        }
        binding["producerFilesAfter"] = binding["producerFilesBefore"]
        binding_path = evidence_path / "build-and-validate-binding.json"
        binding_path.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    "[REPORT_START]",
                    "# BUILD & VALIDATION REPORT",
                    "",
                    f"Solution: {FIXTURE_ROOT.name}",
                    f"Toolkit root: {toolkit_root}",
                    f"Content root: {content_root}",
                    f"Evidence: {evidence_path}",
                    f"Validation binding: {binding_path}",
                    "Validation binding SHA256: "
                    + arm_acceptance.hashlib.sha256(binding_path.read_bytes()).hexdigest(),
                    f"Validation binding result: {result}",
                    "Result: " + result,
                    "",
                    "## Validation Results",
                    "| Step | Validator | Status | Details |",
                    "|------|-----------|--------|---------|",
                    *table,
                    "",
                    "## Summary",
                    summary,
                    "",
                    "**BUILD SUCCESSFUL**" if result == "PASSED" else "**BUILD FAILED**",
                    "[REPORT_END]",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return toolkit_root, report_path, package_report_path, package_identity, created_package_files

    def _cleanup_build_validation_fixture(
        self, toolkit_root, package_report_path, created_package_files
    ):
        shutil.rmtree(toolkit_root, ignore_errors=True)
        shutil.rmtree(package_report_path.parent, ignore_errors=True)
        for path in created_package_files:
            path.unlink(missing_ok=True)

    def test_build_validation_receipt_is_exact_complete_fresh_and_preserves_skips(self):
        toolkit_root, report_path, package_report_path, package_identity, created = (
            self._write_build_validation_receipt()
        )
        try:
            result = arm_acceptance._parse_build_validation_receipt(
                FIXTURE_ROOT,
                report_path,
                package_report_path=package_report_path,
                package_identity=package_identity,
            )
            self.assertEqual("PASSED", result["status"])
            self.assertEqual(1, result["validatorSummary"]["passed"])
            self.assertEqual(1, result["validatorSummary"]["skipped"])
            self.assertEqual("SKIP", result["validatorResults"][1]["status"])
            self.assertEqual(
                arm_acceptance.hashlib.sha256(report_path.read_bytes()).hexdigest(),
                result["sha256"],
            )

            report_path.write_text(
                report_path.read_text(encoding="utf-8").replace(
                    f"Content root: {FIXTURE_ROOT.parent.resolve()}",
                    f"Content root: {FIXTURE_ROOT.resolve()}",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "content root"):
                arm_acceptance._parse_build_validation_receipt(
                    FIXTURE_ROOT,
                    report_path,
                    package_report_path=package_report_path,
                    package_identity=package_identity,
                )
        finally:
            self._cleanup_build_validation_fixture(toolkit_root, package_report_path, created)

    def test_windows_path_order_is_consumed_cross_host_from_recorded_semantics(self):
        source_paths = [
            "Solutions/New-CloudShell/Analytic Rules/rule.yaml",
            "Solutions/azure NRT/Data Connectors/connector.json",
            "Solutions/azure NRT/Data/Solution.json",
        ]
        windows_paths = sorted(source_paths, key=PureWindowsPath)
        posix_paths = sorted(source_paths, key=PurePosixPath)
        self.assertNotEqual(posix_paths, windows_paths)
        self.assertTrue(_source_paths_in_order(windows_paths, "windows"))
        self.assertFalse(_source_paths_in_order(posix_paths, "windows"))
        self.assertTrue(_source_paths_in_order(posix_paths, "posix"))
        with self.assertRaisesRegex(ValueError, "platform-neutral"):
            _source_paths_in_order(windows_paths, "platform-neutral")

        toolkit_root, report_path, package_report_path, package_identity, created = (
            self._write_build_validation_receipt(
                source_path_semantics="windows",
                producer_platform="posix",
            )
        )
        try:
            receipt = arm_acceptance._parse_build_validation_receipt(
                FIXTURE_ROOT,
                report_path,
                package_report_path=package_report_path,
                package_identity=package_identity,
            )
            self.assertEqual("windows", receipt["sourcePathSemantics"])
            self.assertEqual("posix", receipt["producerPlatform"])
        finally:
            self._cleanup_build_validation_fixture(toolkit_root, package_report_path, created)

    def test_build_validation_receipt_rejects_skipped_failed_and_copied_bindings(self):
        toolkit_root, report_path, package_report_path, package_identity, created = (
            self._write_build_validation_receipt(
            rows=[],
            summary="Total: 0 validators | 0 passed | 0 failed | 0 skipped",
            )
        )
        try:
            with self.assertRaisesRegex(ValueError, "no completed validator results"):
                arm_acceptance._parse_build_validation_receipt(
                    FIXTURE_ROOT,
                    report_path,
                    package_report_path=package_report_path,
                    package_identity=package_identity,
                )

            failed_rows = [
                "| TS | TypeScript validators | FAIL | 1 failed |",
            ]
            report_path.write_text(
                "\n".join(
                    [
                        "[REPORT_START]",
                        "# BUILD & VALIDATION REPORT",
                        f"Solution: {FIXTURE_ROOT.name}",
                        f"Toolkit root: {toolkit_root}",
                        f"Content root: {FIXTURE_ROOT.parent.resolve()}",
                        f"Evidence: {report_path.parent}",
                        "Result: FAILED",
                        *failed_rows,
                        "Total: 1 validators | 0 passed | 1 failed | 0 skipped",
                        "**BUILD FAILED**",
                        "[REPORT_END]",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "did not report success"):
                arm_acceptance._parse_build_validation_receipt(
                    FIXTURE_ROOT,
                    report_path,
                    package_report_path=package_report_path,
                    package_identity=package_identity,
                )

            self._cleanup_build_validation_fixture(toolkit_root, package_report_path, created)
            toolkit_root, report_path, package_report_path, package_identity, created = (
                self._write_build_validation_receipt()
            )
            copied_binding = report_path.parent.parent / "copied" / "build-and-validate-binding.json"
            copied_binding.parent.mkdir(parents=True, exist_ok=True)
            copied_binding.write_bytes(
                (report_path.parent / "build-and-validate-binding.json").read_bytes()
            )
            report_path.write_text(
                report_path.read_text(encoding="utf-8").replace(
                    str(report_path.parent / "build-and-validate-binding.json"),
                    str(copied_binding),
                ).replace(
                    arm_acceptance.hashlib.sha256(
                        (report_path.parent / "build-and-validate-binding.json").read_bytes()
                    ).hexdigest(),
                    arm_acceptance.hashlib.sha256(copied_binding.read_bytes()).hexdigest(),
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "copied or is outside"):
                arm_acceptance._parse_build_validation_receipt(
                    FIXTURE_ROOT,
                    report_path,
                    package_report_path=package_report_path,
                    package_identity=package_identity,
                )
        finally:
            self._cleanup_build_validation_fixture(toolkit_root, package_report_path, created)

    def test_build_validation_binding_rejects_a_changed_current_package_identity(self):
        toolkit_root, report_path, package_report_path, package_identity, created = (
            self._write_build_validation_receipt()
        )
        changed_identity = dict(package_identity)
        changed_identity["packageArtifactsSha256"] = "0" * 64
        try:
            with self.assertRaisesRegex(ValueError, "package report identity"):
                arm_acceptance._parse_build_validation_receipt(
                    FIXTURE_ROOT,
                    report_path,
                    package_report_path=package_report_path,
                    package_identity=changed_identity,
                )
            changed_version = dict(package_identity)
            changed_version["version"] = "3.2.0"
            with self.assertRaisesRegex(ValueError, "package report identity"):
                arm_acceptance._parse_build_validation_receipt(
                    FIXTURE_ROOT,
                    report_path,
                    package_report_path=package_report_path,
                    package_identity=changed_version,
                )
        finally:
            self._cleanup_build_validation_fixture(toolkit_root, package_report_path, created)

    def test_package_plan_requires_current_qualification_v31_and_sets_each_flag_true(self):
        template = {
            "parameters": {
                "workspace": {"type": "string"},
                **{
                    name: {"type": "bool", "defaultValue": False}
                    for name in FLAGS
                },
                "environment": {"type": "string", "defaultValue": "public"},
            },
            "resources": [],
        }
        template_text = json.dumps(template)
        template_path = FIXTURE_ROOT / "Package" / "mainTemplate.json"
        original_read_bytes = Path.read_bytes
        def read_bytes(path):
            if path == template_path:
                return template_text.encode()
            return original_read_bytes(path)

        with (
            mock.patch.object(Path, "read_bytes", read_bytes),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.workflow_status",
                return_value=self._state(),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.require_locked_target",
                return_value=TARGET,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._current_package",
                return_value=self._current_package(
                    template_hash=arm_acceptance.hashlib.sha256(
                        template_text.encode()
                    ).hexdigest()
                ),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.resolve_artifact_reference",
                return_value=FIXTURE_ROOT / "Package" / "mainTemplate.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._parse_build_validation_receipt",
                return_value={"status": "PASSED", "sha256": "7" * 64},
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.artifact_path",
                return_value=FIXTURE_ROOT / "Package" / "acceptance-template-snapshot.json",
            ),
            mock.patch("sentinel_xdr_migration.arm_acceptance._write_template_snapshot"),
        ):
            plan = _acceptance_package_plan(FIXTURE_ROOT, VALIDATION_RECEIPTS[0])

        self.assertEqual("ready", plan["status"])
        self.assertEqual(FLAGS, plan["declaredContentFlags"])
        self.assertEqual("arm-acceptance-fixture-ws", plan["parameters"]["workspace"])
        for name in FLAGS:
            self.assertIs(plan["parameters"][name], True)
        self.assertNotIn("environment", plan["parameters"])
        self.assertFalse(plan["resourceReadbackRequired"])
        self.assertFalse(plan["installationVerified"])
        self.assertEqual("PASSED", plan["validationReceipt"]["status"])
        self.assertEqual(template_path.as_posix(), plan["mainTemplatePath"])
        self.assertEqual(
            arm_acceptance.hashlib.sha256(template_text.encode()).hexdigest(),
            plan["mainTemplateSnapshotSha256"],
        )
        self.assertEqual(4, len(plan["packageIdentity"]["packageArtifactHashes"]))

    def test_package_plan_rejects_stale_template_and_required_unbound_parameters(self):
        template_path = FIXTURE_ROOT / "Package" / "mainTemplate.json"
        actual = template_path.read_bytes()
        template_text = json.dumps(
            {
                "parameters": {
                    "workspace": {"type": "string"},
                    "requiredName": {"type": "string"},
                    **{name: {"type": "bool"} for name in FLAGS},
                },
                "resources": [],
            }
        )

        def read_bytes(path):
            return template_text.encode() if path == template_path else actual

        shared = (
            mock.patch.object(Path, "read_bytes", read_bytes),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.workflow_status",
                return_value=self._state(),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.require_locked_target",
                return_value=TARGET,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.resolve_artifact_reference",
                return_value=FIXTURE_ROOT / "Package" / "mainTemplate.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._parse_build_validation_receipt",
                return_value={"status": "PASSED", "sha256": "7" * 64},
            ),
        )
        with shared[0], shared[1], shared[2], shared[3], shared[4]:
            with mock.patch(
                "sentinel_xdr_migration.arm_acceptance._current_package",
                return_value=self._current_package(template_hash="a" * 64),
            ):
                with self.assertRaisesRegex(ValueError, "no longer matches"):
                    _acceptance_package_plan(FIXTURE_ROOT, VALIDATION_RECEIPTS[0])

        # A fresh hash still cannot hide an undeclared, required package parameter.
        fresh_hash = arm_acceptance.hashlib.sha256(template_text.encode()).hexdigest()
        with shared[0], shared[1], shared[2], shared[3], shared[4]:
            with mock.patch(
                "sentinel_xdr_migration.arm_acceptance._current_package",
                return_value=self._current_package(template_hash=fresh_hash),
            ):
                with self.assertRaisesRegex(ValueError, "no default"):
                    _acceptance_package_plan(FIXTURE_ROOT, VALIDATION_RECEIPTS[0])

    def test_batch_plan_requires_exact_same_workstream_flags_but_allows_zero_flag_members(self):
        package_plan = self._package_plan()
        package_plan["declaredContentFlags"] = FLAGS
        package_plan["parameters"] = {
            "workspace": "arm-acceptance-fixture-ws",
            **FLAGS,
        }
        package_plan["parametersSha256"] = arm_acceptance._canonical_sha256(
            package_plan["parameters"]
        )
        receipt = {"decisions": {"knownFlagSelections": FLAGS}}
        binding = {"sha256": "e" * 64, "solutions": ["FixtureOne"]}
        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=NORMALIZED_MEMBERS,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._acceptance_package_plan",
                return_value=package_plan,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_shared_decisions",
                return_value=(receipt, binding),
            ),
        ):
            batch = _arm_acceptance_batch_plan(
                MEMBERS,
                shared_decisions_path=Path("shared-decisions.json"),
                validation_receipts=VALIDATION_RECEIPTS,
            )
        self.assertEqual("ready", batch["status"])
        self.assertEqual(FLAGS, batch["members"][0]["declaredContentFlags"])
        self.assertFalse(batch["environmentWritesAuthorized"])
        self.assertFalse(batch["resourceReadbackRequired"])

        package_plan["declaredContentFlags"] = {}
        package_plan["parameters"] = {"workspace": "arm-acceptance-fixture-ws"}
        package_plan["parametersSha256"] = arm_acceptance._canonical_sha256(
            package_plan["parameters"]
        )
        receipt = {"decisions": {"knownFlagSelections": {}}}
        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=NORMALIZED_MEMBERS,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._acceptance_package_plan",
                return_value=package_plan,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_shared_decisions",
                return_value=(receipt, binding),
            ),
        ):
            empty_batch = _arm_acceptance_batch_plan(
                MEMBERS,
                shared_decisions_path=Path("shared-decisions.json"),
                validation_receipts=VALIDATION_RECEIPTS,
            )
        self.assertEqual({}, empty_batch["members"][0]["declaredContentFlags"])

        receipt = {
            "decisions": {
                "knownFlagSelections": {
                    **FLAGS,
                    "DeployAnalyticsRule": False,
                    "InventedFlag": True,
                }
            }
        }
        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=NORMALIZED_MEMBERS,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._acceptance_package_plan",
                return_value=package_plan,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_shared_decisions",
                return_value=(receipt, binding),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "exactly enumerate"):
                _arm_acceptance_batch_plan(
                    MEMBERS,
                    shared_decisions_path=Path("shared-decisions.json"),
                    validation_receipts=VALIDATION_RECEIPTS,
                )

    def test_batch_plan_refuses_members_from_different_locked_labs(self):
        second_member = {
            "solution": "FixtureTwo",
            "solutionPath": str(FIXTURE_ROOT),
            "runId": RUN_ID + "-2",
        }
        second_plan = self._package_plan()
        second_plan["runId"] = second_member["runId"]
        second_plan["target"] = {**TARGET, "resourceGroup": "other-rg"}
        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=[*NORMALIZED_MEMBERS, second_member],
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._acceptance_package_plan",
                side_effect=[self._package_plan(), second_plan],
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_shared_decisions"
            ) as shared,
        ):
            with self.assertRaisesRegex(ValueError, "cannot cross locked lab targets"):
                _arm_acceptance_batch_plan(
                    [*MEMBERS, second_member],
                    shared_decisions_path=Path("shared-decisions.json"),
                    validation_receipts=[*VALIDATION_RECEIPTS, VALIDATION_RECEIPTS[0]],
                )
        shared.assert_not_called()

    def _execute(
        self,
        response,
        *,
        code=0,
        current_plan=None,
        member_count=1,
        account_check=None,
        runner_side_effect=None,
    ):
        batch = self._batch_plan()
        if member_count == 2:
            second = dict(batch["members"][0])
            second.update(
                {
                    "solution": "FixtureTwo",
                    "runId": RUN_ID + "-2",
                    "deploymentName": "sentinel-arm-fixture-deployment-two",
                }
            )
            batch["members"].append(second)
        current = current_plan or batch
        normalized = [
            {
                "solution": item["solution"],
                "solutionPath": str(FIXTURE_ROOT),
                "runId": item["runId"],
            }
            for item in batch["members"]
        ]
        receipt_path = FIXTURE_ROOT / "no-write-arm-acceptance-receipt.json"
        persisted: list[dict] = []

        def write(_root, _path, value):
            persisted.append(json.loads(json.dumps(value)))

        if runner_side_effect is not None:
            runner = mock.Mock(side_effect=runner_side_effect)
        elif isinstance(response, list):
            runner = mock.Mock(side_effect=response)
        else:
            runner = mock.Mock(
                return_value=(code, response, "fixture CLI error" if code else "")
            )
        patches = (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._arm_acceptance_batch_plan",
                side_effect=[batch, batch, *([current] if current_plan else []), *([batch] * 8)],
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=normalized,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.existing_artifact_path",
                return_value=receipt_path,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.artifact_path",
                return_value=receipt_path,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._member_attempt_path",
                return_value=FIXTURE_ROOT / "no-write-member-attempt.json",
            ),
            mock.patch("sentinel_xdr_migration.arm_acceptance._reserve_attempt"),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.write_json_artifact",
                side_effect=write,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.using_run",
                side_effect=lambda *_args, **_kwargs: nullcontext(),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._verify_existing_cli_target",
                return_value=account_check
                or {
                    "statusCode": 0,
                    "tenantMatches": True,
                    "subscriptionMatches": True,
                },
            ),
            mock.patch(
                "sentinel_xdr_migration.graph_client_config.configured_azure_cli_profile",
                return_value=Path("."),
            ),
            mock.patch(
                "sentinel_xdr_migration.graph_client_config.azure_cli_profile",
                side_effect=lambda _profile: nullcontext(),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._run_cli",
                side_effect=runner,
            ),
        )
        with (
            patches[0],
            patches[1],
            patches[2],
            patches[3],
            patches[4],
            patches[5] as reserve,
            patches[6],
            patches[7],
            patches[8],
            patches[9],
            patches[10],
            patches[11],
        ):
            result = execute_arm_template_acceptance_batch(
                MEMBERS,
                expected_batch_plan_sha256=batch["batchPlanSha256"],
                shared_decisions_path=Path("shared-decisions.json"),
                validation_receipts=VALIDATION_RECEIPTS,
                actor="approved maintainer",
                confirmation=_BATCH_ARM_ACCEPTANCE_CONFIRMATION,
            )
        return result, runner, persisted, reserve

    def test_success_requires_only_terminal_succeeded_and_intent_precedes_cli(self):
        snapshot_path = FIXTURE_ROOT / "Package" / "acceptance-template-snapshot.json"
        original_template = FIXTURE_ROOT / "Package" / "mainTemplate.json"
        original_bytes = original_template.read_bytes()

        def mutate_original_during_submission(command, **_kwargs):
            original_template.write_bytes(b'{"changed":true}')
            try:
                submitted_path = Path(command[command.index("--template-file") + 1])
                submitted_bytes = submitted_path.read_bytes()
                return (
                    1,
                    {
                        "id": "/subscriptions/fixture/resourceGroups/fixture-rg/providers/Microsoft.Resources/deployments/sentinel-arm",
                        "properties": {"provisioningState": "Succeeded"},
                    },
                    "",
                ) if submitted_bytes == snapshot_path.read_bytes() else (1, None, "snapshot mismatch")
            finally:
                original_template.write_bytes(original_bytes)

        try:
            result, runner, persisted, reserve = self._execute(
                {
                    "id": "/subscriptions/fixture/resourceGroups/fixture-rg/providers/Microsoft.Resources/deployments/sentinel-arm",
                    "properties": {"provisioningState": "Succeeded"},
                },
                code=1,
                runner_side_effect=mutate_original_during_submission,
            )
        finally:
            original_template.write_bytes(original_bytes)
        self.assertEqual("accepted", result["status"])
        self.assertEqual("Succeeded", result["members"][0]["provisioningState"])
        self.assertEqual("succeeded", result["members"][0]["normalizedProvisioningState"])
        self.assertEqual(1, result["members"][0]["commandExitCode"])
        self.assertEqual(1, runner.call_count)
        batch_reports = [item for item in persisted if isinstance(item.get("members"), list)]
        self.assertTrue(
            any(item["members"][0]["status"] == "write-intent-persisted" for item in batch_reports)
        )
        self.assertEqual(2, reserve.call_count)
        self.assertFalse(result["resourceReadbackPerformed"])
        self.assertFalse(result["installationVerified"])
        self.assertFalse(result["activationPerformed"])
        command = runner.call_args.args[0]
        self.assertEqual(["deployment", "group", "create"], command[:3])
        self.assertEqual(TARGET["subscriptionId"], command[command.index("--subscription") + 1])
        self.assertEqual(TARGET["resourceGroup"], command[command.index("--resource-group") + 1])
        self.assertEqual(
            str(snapshot_path),
            command[command.index("--template-file") + 1],
        )
        self.assertEqual("Incremental", command[command.index("--mode") + 1])
        self.assertIn("workspace=arm-acceptance-fixture-ws", command)
        for name in FLAGS:
            self.assertIn(f"{name}=true", command)

    def test_terminal_failure_nonterminal_and_timeout_are_persisted_without_retry(self):
        failed, runner, persisted, *_ = self._execute(
            {"id": "deployment-fixture", "properties": {"provisioningState": "Failed"}},
        )
        self.assertEqual("failed", failed["status"])
        self.assertEqual("Failed", failed["members"][0]["provisioningState"])
        self.assertEqual(1, runner.call_count)
        batch_reports = [item for item in persisted if isinstance(item.get("members"), list)]
        self.assertTrue(batch_reports[-1]["retryAuthorized"] is False)

        running, runner, persisted, *_ = self._execute(
            {"id": "deployment-fixture", "properties": {"provisioningState": "Running"}},
        )
        self.assertEqual("nonterminal", running["status"])
        self.assertEqual("Running", running["members"][0]["provisioningState"])
        self.assertEqual(1, runner.call_count)

    def test_partial_batch_result_is_durable_and_stops_after_first_non_succeeded_member(self):
        succeeded = {
            "id": "deployment-fixture-one",
            "properties": {"provisioningState": "Succeeded"},
        }
        failed = {
            "id": "deployment-fixture-two",
            "properties": {"provisioningState": "Failed"},
        }
        result, runner, persisted, *_ = self._execute(
            [
                (0, succeeded, ""),
                (1, failed, "second package failed"),
            ],
            member_count=2,
        )
        self.assertEqual("partial-failed", result["status"])
        self.assertEqual(
            ["accepted", "failed"],
            [member["status"] for member in result["members"]],
        )
        self.assertEqual(
            ["deployment-fixture-one", "deployment-fixture-two"],
            [member["deploymentId"] for member in result["members"]],
        )
        self.assertEqual(2, runner.call_count)
        batch_reports = [item for item in persisted if isinstance(item.get("members"), list)]
        self.assertEqual("partial-failed", batch_reports[-1]["status"])

        unknown, runner, persisted, *_ = self._execute(
            None,
            code=124,
        )
        self.assertEqual("unknown", unknown["status"])
        self.assertIsNone(unknown["members"][0]["deploymentId"])
        self.assertEqual(1, runner.call_count)

    def test_wrong_existing_cli_tenant_or_subscription_blocks_without_write_intent(self):
        result, runner, persisted, reserve = self._execute(
            None,
            account_check={
                "statusCode": 0,
                "tenantMatches": True,
                "subscriptionMatches": False,
                "error": None,
            },
        )
        self.assertEqual("blocked", result["status"])
        self.assertFalse(result["writeAttempted"])
        self.assertEqual(0, runner.call_count)
        self.assertFalse(persisted)
        reserve.assert_not_called()

    def test_changed_batch_hash_before_member_write_is_recorded_without_submit(self):
        changed = self._batch_plan()
        changed["batchPlanSha256"] = "f" * 64
        result, runner, persisted, *_ = self._execute(
            None,
            current_plan=changed,
        )
        self.assertEqual("blocked", result["status"])
        self.assertEqual("blocked-before-write", result["members"][0]["status"])
        self.assertEqual(0, runner.call_count)
        self.assertTrue(persisted)

    def test_mismatched_approval_or_existing_attempt_refuses_before_account_check(self):
        batch = self._batch_plan()
        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._arm_acceptance_batch_plan",
                return_value=batch,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=NORMALIZED_MEMBERS,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.using_run",
                side_effect=lambda *args, **kwargs: nullcontext(),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.artifact_path",
                return_value=FIXTURE_ROOT / "missing-acceptance-report.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.existing_artifact_path",
                return_value=FIXTURE_ROOT / "missing-acceptance-report.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._member_attempt_path",
                return_value=FIXTURE_ROOT / "missing-member-attempt.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._verify_existing_cli_target"
            ) as account_check,
        ):
            with self.assertRaisesRegex(ValueError, "exact enumerated"):
                execute_arm_template_acceptance_batch(
                    MEMBERS,
                    expected_batch_plan_sha256="f" * 64,
                    shared_decisions_path="shared-decisions.json",
                    validation_receipts=VALIDATION_RECEIPTS,
                    actor="approved maintainer",
                    confirmation=_BATCH_ARM_ACCEPTANCE_CONFIRMATION,
                )
            account_check.assert_not_called()

        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._arm_acceptance_batch_plan",
                return_value=batch,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=NORMALIZED_MEMBERS,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.using_run",
                side_effect=lambda *args, **kwargs: nullcontext(),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.artifact_path",
                return_value=FIXTURE_ROOT / "missing-acceptance-report.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.existing_artifact_path",
                return_value=FIXTURE_ROOT / "missing-acceptance-report.json",
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._member_attempt_path",
                return_value=Path(__file__),
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._verify_existing_cli_target"
            ) as account_check,
        ):
            with self.assertRaisesRegex(ValueError, "attempt already exists"):
                execute_arm_template_acceptance_batch(
                    MEMBERS,
                    expected_batch_plan_sha256=batch["batchPlanSha256"],
                    shared_decisions_path="shared-decisions.json",
                    validation_receipts=VALIDATION_RECEIPTS,
                    actor="approved maintainer",
                    confirmation=_BATCH_ARM_ACCEPTANCE_CONFIRMATION,
                )
            account_check.assert_not_called()

    def test_reordered_batch_cannot_retry_a_member_with_an_existing_attempt(self):
        batch = self._batch_plan()
        first = dict(batch["members"][0])
        first.update({"solution": "FixtureA", "runId": RUN_ID + "-a"})
        second = dict(batch["members"][0])
        second.update(
            {
                "solution": "FixtureB",
                "runId": RUN_ID + "-b",
                "deploymentName": "sentinel-arm-fixture-deployment-b",
            }
        )
        batch["members"] = [second, first]
        batch["batchPlanSha256"] = "c" * 64
        normalized = [
            {"solution": item["solution"], "solutionPath": str(FIXTURE_ROOT), "runId": item["runId"]}
            for item in batch["members"]
        ]
        prior_attempt = FIXTURE_ROOT / "prior-member-b-attempt.json"
        central_report = FIXTURE_ROOT / "no-write-arm-acceptance-receipt.json"

        with (
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._arm_acceptance_batch_plan",
                return_value=batch,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._validated_members",
                return_value=normalized,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.existing_artifact_path",
                return_value=central_report,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance.artifact_path",
                return_value=central_report,
            ),
            mock.patch(
                "sentinel_xdr_migration.arm_acceptance._member_attempt_path",
                side_effect=lambda item: (
                    prior_attempt
                    if item["solution"] == "FixtureB"
                    else FIXTURE_ROOT / "unattempted-member-a.json"
                ),
            ),
            mock.patch.object(Path, "exists", autospec=True, side_effect=lambda path: path == prior_attempt),
            mock.patch("sentinel_xdr_migration.arm_acceptance._verify_existing_cli_target") as account,
            mock.patch("sentinel_xdr_migration.arm_acceptance._reserve_attempt") as reserve,
            mock.patch("sentinel_xdr_migration.arm_acceptance._run_cli") as runner,
        ):
            with self.assertRaisesRegex(ValueError, "deployment identity"):
                execute_arm_template_acceptance_batch(
                    [
                        {"solution": "FixtureB", "solutionPath": str(FIXTURE_ROOT), "runId": RUN_ID + "-b"},
                        {"solution": "FixtureA", "solutionPath": str(FIXTURE_ROOT), "runId": RUN_ID + "-a"},
                    ],
                    expected_batch_plan_sha256=batch["batchPlanSha256"],
                    shared_decisions_path="shared-decisions.json",
                    validation_receipts=[VALIDATION_RECEIPTS[0], VALIDATION_RECEIPTS[0]],
                    actor="approved maintainer",
                    confirmation=_BATCH_ARM_ACCEPTANCE_CONFIRMATION,
                )
        account.assert_not_called()
        reserve.assert_not_called()
        runner.assert_not_called()

    def test_cli_surface_registers_separate_acceptance_commands(self):
        from sentinel_xdr_migration import cli

        with mock.patch(
            "sentinel_xdr_migration.cli.plan_arm_template_acceptance_batch",
            return_value={"status": "ready"},
        ) as plan:
            result = cli.main(
                [
                    "plan-arm-template-acceptance-batch",
                    "--member",
                    f"{FIXTURE_ROOT}::{RUN_ID}",
                    "--validation-receipt",
                    VALIDATION_RECEIPTS[0],
                    "--shared-decisions",
                    "shared-decisions.json",
                ]
            )
        self.assertEqual(0, result)
        self.assertEqual(str(FIXTURE_ROOT), plan.call_args.args[0][0]["solution"])
        with mock.patch(
            "sentinel_xdr_migration.cli.execute_arm_template_acceptance_batch",
            return_value={"status": "accepted"},
        ) as execute:
            result = cli.main(
                [
                    "deploy-arm-template-acceptance-batch",
                    "--member",
                    f"{FIXTURE_ROOT}::{RUN_ID}",
                    "--validation-receipt",
                    VALIDATION_RECEIPTS[0],
                    "--shared-decisions",
                    "shared-decisions.json",
                    "--expected-batch-plan-sha256",
                    "b" * 64,
                    "--actor",
                    "approved maintainer",
                    "--confirm-exact-scope-write",
                    _BATCH_ARM_ACCEPTANCE_CONFIRMATION,
                ]
            )
        self.assertEqual(0, result)
        self.assertEqual(str(FIXTURE_ROOT), execute.call_args.args[0][0]["solution"])

        with (
            mock.patch(
                "sentinel_xdr_migration.cli.execute_arm_template_acceptance_batch",
                return_value={"status": "unknown"},
            ),
            redirect_stdout(StringIO()),
        ):
            failed_result = cli.main(
                [
                    "deploy-arm-template-acceptance-batch",
                    "--member",
                    f"{FIXTURE_ROOT}::{RUN_ID}",
                    "--validation-receipt",
                    VALIDATION_RECEIPTS[0],
                    "--shared-decisions",
                    "shared-decisions.json",
                    "--expected-batch-plan-sha256",
                    "b" * 64,
                    "--actor",
                    "approved maintainer",
                    "--confirm-exact-scope-write",
                    _BATCH_ARM_ACCEPTANCE_CONFIRMATION,
                ]
            )
        self.assertEqual(1, failed_result)


if __name__ == "__main__":
    unittest.main()
