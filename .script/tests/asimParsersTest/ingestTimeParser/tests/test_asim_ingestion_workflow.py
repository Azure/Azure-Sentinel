import importlib.util
import io
import json
import sys
import tempfile
import unittest
import unittest.mock
from contextlib import redirect_stdout
from pathlib import Path

import yaml


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "asim_ingestion_workflow.py"
)
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location(
    "asim_ingestion_workflow", MODULE_PATH
)
WORKFLOW = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WORKFLOW
SPEC.loader.exec_module(WORKFLOW)


def target(
    target_id,
    *,
    source_table="Contoso_CL",
    target_table="ASimAuthenticationEventLogs",
    fixture="Sample Data/ASIM/Contoso_Contoso_Authentication_"
    "Contoso_CL_IngestedLogs.csv",
):
    return {
        "targetId": target_id,
        "triggerPaths": [
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            f"{target_id}.yaml"
        ],
        "validationKind": "paired",
        "pairStatus": "paired",
        "queryTimeParserPath": (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        ),
        "ingestTimeParserPath": (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            f"{target_id}.yaml"
        ),
        "schema": "Authentication",
        "schemaVersion": "1.0.0",
        "product": "Contoso",
        "sourceRawTable": source_table,
        "targetASIMTable": target_table,
        "fixturePath": fixture,
        "fixtureStatus": "resolved",
        "pairCandidates": [],
        "pairEvidence": {},
        "discoveryErrors": [],
    }


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write_fixture(self, relative_path, size=100):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * size)
        return path

    def test_allocates_unique_slots_across_source_and_target_conflicts(self):
        fixture = (
            "Sample Data/ASIM/Contoso_Contoso_Authentication_"
            "Contoso_CL_IngestedLogs.csv"
        )
        self.write_fixture(fixture)
        manifest = {
            "version": 2,
            "targets": [
                target("parser-a", fixture=fixture),
                target(
                    "parser-b",
                    source_table="Other_CL",
                    fixture=fixture,
                ),
                target(
                    "parser-c",
                    fixture=fixture,
                    target_table="ASimAlertEventLogs",
                ),
            ],
        }

        result = WORKFLOW.build_matrix_manifest(
            manifest,
            repo_root=self.root,
            max_targets=25,
            max_fixture_bytes=1024,
        )

        by_id = {
            item["targetId"]: item for item in result["targets"]
        }
        self.assertEqual(0, by_id["parser-a"]["targetSlot"])
        self.assertEqual(1, by_id["parser-b"]["targetSlot"])
        self.assertEqual(2, by_id["parser-c"]["targetSlot"])
        self.assertTrue(
            all(
                item["targetCount"] == 3
                for item in by_id.values()
            )
        )

    def test_marks_oversized_fixture_as_discovery_error(self):
        fixture = (
            "Sample Data/ASIM/Contoso_Contoso_Authentication_"
            "Contoso_CL_IngestedLogs.csv"
        )
        self.write_fixture(fixture, size=11)

        result = WORKFLOW.build_matrix_manifest(
            {"targets": [target("parser-a", fixture=fixture)]},
            repo_root=self.root,
            max_targets=25,
            max_fixture_bytes=10,
        )

        errors = result["targets"][0]["discoveryErrors"]
        self.assertEqual(1, len(errors))
        self.assertIn("exceeds", errors[0])

    def test_rejects_more_than_target_limit(self):
        with self.assertRaisesRegex(
            WORKFLOW.WorkflowContractError, "workflow limit is 2"
        ):
            WORKFLOW.build_matrix_manifest(
                {
                    "targets": [
                        target("parser-a"),
                        target("parser-b"),
                        target("parser-c"),
                    ]
                },
                repo_root=self.root,
                max_targets=2,
                max_fixture_bytes=100,
            )

    def test_rejects_unsafe_repository_path(self):
        unsafe = target("parser-a")
        unsafe["fixturePath"] = (
            "Sample Data/ASIM/../../secret_IngestedLogs.csv"
        )
        with self.assertRaisesRegex(
            WORKFLOW.WorkflowContractError, "Unsafe repository path"
        ):
            WORKFLOW.build_matrix_manifest(
                {"targets": [unsafe]},
                repo_root=self.root,
                max_targets=25,
                max_fixture_bytes=100,
            )

    def test_rejects_wrong_parser_path_kind(self):
        invalid = target("parser-a")
        invalid["ingestTimeParserPath"] = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        with self.assertRaisesRegex(
            WORKFLOW.WorkflowContractError,
            "ingestTimeParserPath has an unsupported",
        ):
            WORKFLOW.build_matrix_manifest(
                {"targets": [invalid]},
                repo_root=self.root,
                max_targets=25,
                max_fixture_bytes=100,
            )

    def test_cli_writes_matrix_outputs(self):
        fixture = (
            "Sample Data/ASIM/Contoso_Contoso_Authentication_"
            "Contoso_CL_IngestedLogs.csv"
        )
        self.write_fixture(fixture)
        manifest_path = self.root / "manifest.json"
        output_path = self.root / "matrix.json"
        github_output = self.root / "github-output.txt"
        manifest_path.write_text(
            json.dumps(
                {"targets": [target("parser-a", fixture=fixture)]}
            ),
            encoding="utf-8",
        )

        exit_code = WORKFLOW.main(
            [
                "matrix",
                "--manifest",
                str(manifest_path),
                "--output",
                str(output_path),
                "--repo-root",
                str(self.root),
                "--github-output",
                str(github_output),
            ]
        )

        self.assertEqual(0, exit_code)
        self.assertTrue(output_path.is_file())
        outputs = github_output.read_text(encoding="utf-8")
        self.assertIn("has_targets=true", outputs)
        self.assertIn('target_ids=["parser-a"]', outputs)


class ExportTests(unittest.TestCase):
    def test_export_target_writes_safe_github_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "target.json"
            github_output = root / "github-output.txt"
            manifest = {
                "targets": [
                    {
                        **target("parser-a"),
                        "targetSlot": 0,
                        "targetCount": 1,
                    }
                ]
            }

            exported = WORKFLOW.export_target(
                manifest,
                "parser-a",
                target_output=output,
                github_output=github_output,
            )

            self.assertEqual("parser-a", exported["targetId"])
            text = github_output.read_text(encoding="utf-8")
            self.assertIn("discovery_valid=true", text)
            self.assertIn("target_slot=0", text)

    def test_export_static_preserves_qtp_blocked_state(self):
        with tempfile.TemporaryDirectory() as directory:
            github_output = Path(directory) / "github-output.txt"
            outputs = WORKFLOW.export_static_decision(
                {
                    "valid": True,
                    "queryTimeEligibility": {"status": "blocked"},
                },
                github_output,
            )

            self.assertEqual("true", outputs["itp_valid"])
            self.assertEqual("false", outputs["qtp_eligible"])

    def test_writes_bounded_workflow_error_result(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "error.json"
            result = WORKFLOW.write_error_result(
                stage="azure-login",
                message="failure\n" + ("x" * 600),
                output=output,
            )

            self.assertEqual("failed", result["status"])
            self.assertEqual(
                "azure-login", result["error"]["stage"]
            )
            self.assertLessEqual(
                len(result["error"]["message"]), 500
            )
            self.assertTrue(output.is_file())


class ReportTests(unittest.TestCase):
    def base_validation(self):
        return {
            "status": "completed",
            "rawDcr": {"resourceId": "/raw"},
            "parserDcr": {"resourceId": "/parser"},
            "rawUpload": [{"status": "accepted"}],
            "parserUpload": [{"status": "accepted"}],
            "snapshot": {"rowCount": 2},
            "filterValidation": {
                "status": "passed",
                "selectedRowCount": 1,
                "rejectedRowCount": 1,
            },
            "outputValidation": {
                "schemaValidation": {"status": "passed"},
                "dataTest": {"status": "passed"},
                "queryTimeExecution": {
                    "status": "passed",
                    "rowCount": 1,
                },
                "parity": {
                    "status": "passed",
                    "rows": {
                        "missingRowCount": 0,
                        "extraRowCount": 0,
                    },
                },
            },
            "cleanup": [
                {"resourceId": "/parser", "status": "deleted"}
            ],
            "telemetry": {
                "elapsedSeconds": 12.3,
                "stageTimingsSeconds": {"filter-validation": 1.2},
            },
        }

    def build(self, validation, *, required=False, cleanup=None):
        return WORKFLOW.build_report(
            target=target("parser-a"),
            static_result={
                "valid": True,
                "findings": [],
                "queryTimeEligibility": {"status": "eligible"},
            },
            prepared_fixture={
                "fixturePath": "fixture.csv",
                "rowCount": 2,
                "namespace": {"timestampSetHash": "sha256:value"},
            },
            validation_result=validation,
            cleanup_result=cleanup,
            repository="Azure/Azure-Sentinel",
            pull_request="123",
            run_id="456",
            run_attempt="1",
            enforcement_required=required,
        )

    def test_success_report_contains_stage_evidence(self):
        report = self.build(self.base_validation())

        self.assertEqual("passed", report["status"])
        self.assertFalse(report["requiredFailure"])
        self.assertEqual(
            "passed", report["stages"]["filtering"]["status"]
        )
        self.assertEqual(
            "passed", report["stages"]["parity"]["status"]
        )
        summary = WORKFLOW.render_summary(report)
        self.assertIn("ASIM ingestion validation", summary)
        self.assertIn("| parity |", summary)

    def test_failure_is_shadow_only_when_not_required(self):
        validation = self.base_validation()
        validation["status"] = "failed"
        validation["error"] = {
            "stage": "parity",
            "message": "rows differ",
            "details": {"missingRowCount": 1},
        }
        validation["outputValidation"] = None

        report = self.build(validation, required=False)

        self.assertEqual("shadow-only-failure", report["status"])
        self.assertTrue(report["requiredFailure"])
        self.assertEqual(
            "failed", report["stages"]["parity"]["status"]
        )

    def test_failure_is_blocking_when_required(self):
        validation = self.base_validation()
        validation["status"] = "failed"
        validation["error"] = {
            "stage": "asim-data",
            "message": "invalid data",
        }
        validation["outputValidation"] = None

        report = self.build(validation, required=True)

        self.assertEqual("failed", report["status"])

    def test_fixture_preparation_error_is_reported(self):
        report = WORKFLOW.build_report(
            target=target("parser-a"),
            static_result={
                "valid": True,
                "findings": [],
                "queryTimeEligibility": {"status": "eligible"},
            },
            prepared_fixture=None,
            validation_result={
                "status": "failed",
                "error": {
                    "stage": "fixture-preparation",
                    "message": "conversion failed",
                },
            },
            cleanup_result=None,
            repository="Azure/Azure-Sentinel",
            pull_request="123",
            run_id="456",
            run_attempt="1",
            enforcement_required=False,
        )

        self.assertEqual(
            "conversion failed",
            report["stages"]["fixture"]["detail"],
        )

    def test_cleanup_warning_does_not_change_parser_result(self):
        report = self.build(
            self.base_validation(),
            cleanup={
                "resources": [
                    {
                        "resourceId": "/raw",
                        "status": "warning",
                        "message": "delete failed",
                    }
                ]
            },
        )

        self.assertEqual("passed", report["status"])
        self.assertEqual(
            "warning", report["stages"]["cleanup"]["status"]
        )

    def test_target_visibility_failure_marks_parser_ingestion_failed(self):
        validation = self.base_validation()
        validation["status"] = "failed"
        validation["error"] = {
            "stage": "target-visibility",
            "message": "timed out",
        }
        validation["outputValidation"] = None

        report = self.build(validation)

        self.assertEqual(
            "failed",
            report["stages"]["parserIngestion"]["status"],
        )
        self.assertEqual(
            "passed", report["stages"]["schema"]["status"]
        )

    def test_parity_failure_records_successful_qtp_execution(self):
        validation = self.base_validation()
        validation["status"] = "failed"
        validation["outputValidation"] = None
        validation["error"] = {
            "stage": "parity",
            "message": "rows differ",
            "details": {"missingRowCount": 1},
        }

        report = self.build(validation)

        self.assertEqual(
            "passed", report["stages"]["qtpExecution"]["status"]
        )
        self.assertEqual(
            "failed", report["stages"]["parity"]["status"]
        )

    def test_annotations_escape_percent_sequences(self):
        validation = self.base_validation()
        validation["status"] = "failed"
        validation["error"] = {
            "stage": "asim-data",
            "message": "invalid %0A value",
        }
        validation["outputValidation"] = None
        report = self.build(validation, required=True)
        output = io.StringIO()

        with redirect_stdout(output):
            WORKFLOW.emit_annotations(report)

        self.assertIn("invalid %250A value", output.getvalue())


class CleanupTests(unittest.TestCase):
    class FakeHarness:
        def __init__(self, config, token_provider, deadline_seconds):
            self.deleted = []

        def dcr_resource_id(self, name):
            return f"/dcr/{name}"

        def delete_dcr(self, resource_id):
            self.deleted.append(resource_id)
            return {
                "resourceId": resource_id,
                "status": "not-found",
            }

    @unittest.mock.patch.object(
        WORKFLOW.workflow_contracts,
        "DefaultAzureTokenProvider",
        return_value=object(),
    )
    @unittest.mock.patch.object(
        WORKFLOW.workflow_contracts,
        "AsimIngestionHarness",
        FakeHarness,
    )
    def test_cleanup_uses_deterministic_raw_and_parser_names(
        self, token_provider
    ):
        result = WORKFLOW.cleanup_target(
            target_id="parser-a",
            pull_request="123",
            run_id="456",
            run_attempt=2,
            config=WORKFLOW.CanaryConfig(),
        )

        names = WORKFLOW.build_resource_names(
            "parser-a", "123", "456", 2
        )
        self.assertEqual("passed", result["status"])
        self.assertEqual(
            [
                f"/dcr/{names['parserDcr']}",
                f"/dcr/{names['rawDcr']}",
            ],
            [
                resource["resourceId"]
                for resource in result["resources"]
            ],
        )
        token_provider.assert_called_once()


class WorkflowTopologyTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[5]
        self.legacy_path = (
            self.repo_root
            / ".github/workflows/runAsimSchemaAndDataTesters.yaml"
        )
        self.isolated_path = (
            self.repo_root
            / ".github/workflows/runAsimIngestionTimeValidation.yaml"
        )

    def test_security_gate_matches_legacy_except_initial_events(self):
        legacy = self.legacy_path.read_text(encoding="utf-8")
        isolated = self.isolated_path.read_text(encoding="utf-8")

        def job_block(text, start_marker, end_marker):
            start = text.index(start_marker)
            end = text.index(end_marker, start)
            return text[start:end]

        legacy_gate = job_block(
            legacy,
            "  security-gate:\n",
            "\n  Run-ASim-TemplateValidation:",
        )
        isolated_gate = job_block(
            isolated,
            "  security-gate:\n",
            "\n  discover:",
        )
        initial_event_branch = """\
            elif [ "$trigger_event" = "opened" ] ||
                 [ "$trigger_event" = "reopened" ]; then
              log_info "Fork PR requires SafeToRun approval"
              echo "approved=false" >> $GITHUB_OUTPUT
              echo "needs_approval=true" >> $GITHUB_OUTPUT
              echo "comment_needed=true" >> $GITHUB_OUTPUT
              exit 1
"""
        self.assertIn(initial_event_branch, isolated_gate)
        isolated_gate = isolated_gate.replace(
            initial_event_branch, "", 1
        )

        normalize = lambda value: "\n".join(
            line.rstrip() for line in value.splitlines()
        )
        self.assertEqual(
            normalize(legacy_gate),
            normalize(isolated_gate),
        )

    def test_isolated_workflow_has_requested_job_topology(self):
        document = yaml.safe_load(
            self.isolated_path.read_text(encoding="utf-8")
        )
        jobs = document["jobs"]

        self.assertEqual(
            [
                "security-gate",
                "discover",
                "templateValidate",
                "ingestionValidation",
                "report",
            ],
            list(jobs),
        )
        self.assertEqual(
            ["security-gate", "discover"],
            jobs["templateValidate"]["needs"],
        )
        self.assertEqual(
            ["security-gate", "discover", "templateValidate"],
            jobs["ingestionValidation"]["needs"],
        )
        self.assertEqual(
            [
                "security-gate",
                "discover",
                "templateValidate",
                "ingestionValidation",
            ],
            jobs["report"]["needs"],
        )

    def test_workflow_has_no_manual_or_pr_head_checkout(self):
        workflow = self.isolated_path.read_text(encoding="utf-8")

        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertNotIn(
            "ref: ${{ github.event.pull_request.head.sha }}",
            workflow,
        )
        self.assertEqual(
            3,
            workflow.count(
                "ref: ${{ github.event.pull_request.base.sha }}"
            ),
        )

    def test_workflow_runs_on_initial_pull_request_events(self):
        workflow = self.isolated_path.read_text(encoding="utf-8")

        self.assertIn(
            "types: [opened, reopened, labeled, synchronize]",
            workflow,
        )
        self.assertIn(
            'elif [ "$trigger_event" = "opened" ] ||',
            workflow,
        )
        self.assertIn(
            '[ "$trigger_event" = "reopened" ]; then',
            workflow,
        )
        self.assertIn(
            'echo "needs_approval=true" >> $GITHUB_OUTPUT',
            workflow,
        )
        self.assertIn(
            'echo "comment_needed=true" >> $GITHUB_OUTPUT',
            workflow,
        )

    def test_untrusted_pr_content_is_materialized_only_as_data(self):
        workflow = self.isolated_path.read_text(encoding="utf-8")

        self.assertEqual(
            2,
            workflow.count(
                "Materialize pull request content as untrusted data"
            ),
        )
        self.assertIn(
            "$ARTIFACT_DIR/ingest-time-parser.yaml",
            workflow,
        )
        self.assertIn(
            "$ARTIFACT_DIR/query-time-parser.yaml",
            workflow,
        )
        self.assertIn(
            '"$ARTIFACT_DIR/ingest-time-parser.yaml"',
            workflow,
        )

    def test_untrusted_pr_content_is_pinned_to_event_head_sha(self):
        workflow = self.isolated_path.read_text(encoding="utf-8")

        self.assertEqual(
            2,
            workflow.count(
                "PR_HEAD_SHA: "
                "${{ github.event.pull_request.head.sha }}"
            ),
        )
        self.assertEqual(
            2,
            workflow.count(
                'if ! [[ "$PR_HEAD_SHA" =~ ^[0-9a-f]{40}$ ]]; then'
            ),
        )
        self.assertEqual(
            2,
            workflow.count(
                'if [ "$fetched_sha" != "$PR_HEAD_SHA" ]; then'
            ),
        )
        self.assertEqual(
            2,
            workflow.count(
                '"$pr_data_dir" "$PR_HEAD_SHA"'
            ),
        )

    def test_trusted_helper_package_is_restored_from_master(self):
        workflow = self.isolated_path.read_text(encoding="utf-8")

        self.assertEqual(
            3,
            workflow.count("git archive origin/master"),
        )
        self.assertGreaterEqual(
            workflow.count(
                ".script/tests/asimParsersTest/ingestTimeParser"
            ),
            6,
        )
        self.assertNotIn("ingestTimeParser/$helper", workflow)


if __name__ == "__main__":
    unittest.main()
