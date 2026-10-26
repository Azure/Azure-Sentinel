from __future__ import annotations

import datetime
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration import cli as cli_module
from sentinel_xdr_migration import release_notes as release_notes_module
from sentinel_xdr_migration import workflow as workflow_module
from sentinel_xdr_migration.artifacts import using_run
from sentinel_xdr_migration.packaging import package_input_identity
from sentinel_xdr_migration.release_notes import (
    default_release_date,
    release_notes_refresh_proposal,
    resolve_release_date,
)
from sentinel_xdr_migration.workflow import (
    complete_workflow_stage,
    initialize_workflow,
    package_workflow_v3_1,
    plan_new_package_release,
    plan_release_notes_refresh,
)


class ReleaseNotesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.solution = Path(self.temp.name) / "Sample"
        self.solution.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_release_notes(self) -> Path:
        notes = self.solution / "ReleaseNotes.md"
        separator = "|---------|-------------------------------|----------------|\n"
        notes.write_text(
            "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
            + separator
            + "| 3.2.1 | 01-10-2026 | Prior release. |\n"
            + "| 3.2.0 | 01-09-2026 | Older release. |\n",
            encoding="utf-8",
        )
        return notes

    def test_default_release_date_returns_dd_mm_yyyy(self) -> None:
        fixed_date = datetime.date(2026, 4, 19)
        self.assertEqual("19-04-2026", default_release_date(today=fixed_date))
        self.assertEqual("19-04-2026", resolve_release_date(None, today=fixed_date))
        self.assertEqual("19-04-2026", resolve_release_date("   ", today=fixed_date))

    def test_resolve_release_date_honors_explicit_override_and_rejects_invalid(self) -> None:
        self.assertEqual("05-11-2026", resolve_release_date("05-11-2026"))
        with self.assertRaisesRegex(ValueError, "release date must be a valid DD-MM-YYYY"):
            resolve_release_date("2026-11-05")
        with self.assertRaisesRegex(ValueError, "release date must be a valid DD-MM-YYYY"):
            resolve_release_date("31-02-2026")

    def test_release_notes_refresh_proposal_defaults_to_today_and_supports_override(self) -> None:
        notes = self._write_release_notes()
        fixed_date = datetime.date(2026, 4, 19)

        path, before_sha, after_sha, resolved_date = release_notes_refresh_proposal(
            self.solution,
            version="3.2.2",
            release_date=None,
            change_history="Added converted Defender XDR detections.",
            today=fixed_date,
        )
        self.assertEqual(notes, path)
        self.assertEqual("19-04-2026", resolved_date)
        self.assertNotEqual(before_sha, after_sha)

        _, _, override_after_sha, override_date = release_notes_refresh_proposal(
            self.solution,
            version="3.2.2",
            release_date="25-12-2026",
            change_history="Added converted Defender XDR detections.",
            today=fixed_date,
        )
        self.assertEqual("25-12-2026", override_date)
        self.assertNotEqual(after_sha, override_after_sha)

    def test_workflow_plan_release_notes_refresh_defaults_to_today_and_cli_allows_omitting_date(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        data.parent.mkdir(parents=True)
        data.write_text(json.dumps({"Name": "Sample", "Version": "3.2.1"}), encoding="utf-8")
        self._write_release_notes()
        from test_converter import RULE
        source_dir = self.solution / "Analytic Rules"
        source_dir.mkdir(parents=True)
        source_rule = source_dir / "Rule.yaml"
        source_rule.write_text(RULE, encoding="utf-8")

        initialized = initialize_workflow(
            self.solution,
            version_bump="none",
            target_version="3.2.2",
            workflow_profile="authoring",
            campaign_id="release-notes-default-date",
        )
        run_id = initialized["runId"]

        def fake_package(solution: Path, **kwargs: str) -> dict:
            before_identity = package_input_identity(solution)
            target_ver = kwargs.get("target_version") or "3.2.2"
            data.write_text(json.dumps({"Name": "Sample", "Version": target_ver}), encoding="utf-8")
            package_dir = solution / "Package"
            package_dir.mkdir(exist_ok=True)
            paths = {
                "mainTemplate": package_dir / "mainTemplate.json",
                "createUiDefinition": package_dir / "createUiDefinition.json",
                "testParameters": package_dir / "testParameters.json",
                "zip": package_dir / f"{target_ver}.zip",
            }
            for path in paths.values():
                path.write_text("{}", encoding="utf-8")
            from sentinel_xdr_migration.artifacts import artifact_path
            from sentinel_xdr_migration.packaging import package_input_file_hashes
            report = artifact_path(solution, "packaging.v3_1.json", create_parent=True)
            after_identity = package_input_identity(solution)
            package_hashes = {
                name: hashlib.sha256(path.read_bytes()).hexdigest()
                for name, path in paths.items()
            }
            payload = {
                "status": "passed",
                "packager": "V3.1",
                "version": target_ver,
                "versionBump": kwargs.get("version_bump", "none"),
                "requestedVersionBump": kwargs.get("requested_version_bump", "none"),
                "effectiveVersionBump": kwargs.get("version_bump", "none"),
                "requestedTargetVersion": target_ver,
                "effectiveTargetVersion": target_ver,
                "packageAttemptId": kwargs.get("package_attempt_id"),
                "workflowRunId": kwargs.get("workflow_run_id"),
                "packageInputs": {
                    "before": before_identity,
                    "after": {**after_identity, "files": package_input_file_hashes(solution)},
                },
                "packageArtifactHashes": package_hashes,
                "packageArtifactsSha256": hashlib.sha256(
                    json.dumps(package_hashes, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                "packageReport": str(report),
                "workflowArtifacts": {
                    "packager": "V3.1",
                    "packageReport": str(report),
                    **{k: str(v) for k, v in paths.items()},
                },
                **{k: str(v) for k, v in paths.items()},
            }
            report.write_text(json.dumps(payload), encoding="utf-8")
            return payload

        with using_run(self.solution, run_id):
            from sentinel_xdr_migration.converter import convert_solution
            import hashlib
            workflow_module.start_workflow_stage(self.solution, "discovery")
            complete_workflow_stage(self.solution, "discovery", status="passed")
            workflow_module.start_workflow_stage(self.solution, "conversion")
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
            workflow_module.start_workflow_stage(self.solution, "validation")
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={"runtimeStatus": "not-run", "validationMode": "offline-authoring"},
            )
            plan_new_package_release(
                self.solution,
                target_version="3.2.2",
                expected_package_input_sha256=package_input_identity(self.solution)["sha256"],
            )
            with mock.patch.object(workflow_module, "package_solution_v3_1", side_effect=fake_package):
                package_workflow_v3_1(
                    self.solution,
                    requested_version_bump="none",
                    requested_target_version="3.2.2",
                )

            base_hash = package_input_identity(self.solution)["sha256"]
            with mock.patch.object(
                release_notes_module,
                "default_release_date",
                return_value="19-04-2026",
            ):
                refresh = plan_release_notes_refresh(
                    self.solution,
                    change_history="Default date release notes entry.",
                    expected_package_input_sha256=base_hash,
                )
            self.assertEqual("19-04-2026", refresh["releaseDate"])

        expected_hash = "d" * 64
        with mock.patch.object(cli_module, "configure_logging"), mock.patch.object(
            cli_module,
            "plan_release_notes_refresh",
            return_value={"releaseDate": "19-04-2026", "packageInputSha256Before": expected_hash},
        ) as cli_refresh:
            rc = cli_module.main([
                "workflow-plan-release-notes-refresh",
                "--solution", str(self.solution),
                "--run-id", run_id,
                "--change-history", "CLI omitted release date.",
                "--expected-package-input-sha256", expected_hash,
            ])
        self.assertEqual(0, rc)
        cli_refresh.assert_called_once_with(
            str(self.solution),
            release_date=None,
            change_history="CLI omitted release date.",
            expected_package_input_sha256=expected_hash,
        )


if __name__ == "__main__":
    unittest.main()
