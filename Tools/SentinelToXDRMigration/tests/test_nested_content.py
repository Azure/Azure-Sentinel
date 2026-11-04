from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.alert_parity import _load_pairs, start_alert_parity_batch
from sentinel_xdr_migration.analytic_deployment import deploy_analytic_rules
from sentinel_xdr_migration.content_paths import content_path, detection_reference
from sentinel_xdr_migration.converter import (
    analytic_rule_files,
    convert_solution,
    inspect_solution,
    runtime_validation_plan,
    validate_solution,
    xdr_detection_files,
)
from sentinel_xdr_migration.deployment import deploy_solution
from sentinel_xdr_migration.packaging import _xdr_references
from sentinel_xdr_migration.runtime import record_runtime_validation, validate_advanced_hunting
from sentinel_xdr_migration.solution_report import build_solution_report


class NestedContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.solution = Path(self.temp.name) / "Solutions" / "Nested"
        self.analytic = self.solution / "Analytic Rules"
        self.output = self.solution / "XDR Detections"
        self.names = sorted([
            "SampleRule.yaml",
            "Execution/SampleRule.yaml",
            "Execution/Deep/Rule.yml",
            "Persistence/SampleRule.yaml",
            "Root.YAML",
        ])
        for name in self.names:
            path = self.analytic / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, name)),
                "name": f"Test {name}",
                "description": "Detect test activity",
                "kind": "Scheduled",
                "version": "1.0.0",
                "severity": "High",
                "queryFrequency": "1h",
                "queryPeriod": "1h",
                "query": "DeviceEvents | project TimeGenerated, AccountUpn",
                "entityMappings": [{
                    "entityType": "Account",
                    "fieldMappings": [{"identifier": "Upn", "columnName": "AccountUpn"}],
                }],
            }), encoding="utf-8")

    def test_recursive_conversion_preserves_paths_versions_and_source_bytes(self) -> None:
        sources = {path: path.read_bytes() for path in analytic_rule_files(self.solution)}
        self.assertEqual(self.names, inspect_solution(self.solution)["analyticRules"])
        result = convert_solution(self.solution)
        self.assertEqual(len(self.names), result["converted"])
        self.assertEqual(self.names, [
            path.relative_to(self.output).as_posix()
            for path in xdr_detection_files(self.output)
        ])
        references = []
        for item in result["results"]:
            relative = item["sourceRelativePath"].removeprefix("Analytic Rules/")
            self.assertEqual(f"XDR Detections/{relative}", item["outputRelativePath"])
            document = yaml.safe_load((self.output / relative).read_text())
            self.assertEqual(item["sourceRelativePath"], document["contentProvenance"]["source"]["path"])
            self.assertEqual("3.1.0", document["version"])
            self.assertEqual("1.0.0", document["contentProvenance"]["source"]["version"])
            references.append(item["outputRelativePath"])
        self.assertEqual(
            xdr_detection_files(self.output),
            _xdr_references(self.solution, {"XDR Detections": references}),
        )
        self.assertEqual(
            xdr_detection_files(self.output),
            _xdr_references(self.solution, {"XDR Detections": [p.replace("/", "\\") for p in references]}),
        )
        first = {path: path.read_bytes() for path in xdr_detection_files(self.output)}
        modification_times = {path: path.stat().st_mtime_ns for path in first}
        repeated = convert_solution(self.solution)
        self.assertEqual(0, repeated["conflicts"])
        self.assertEqual(first, {path: path.read_bytes() for path in first})
        self.assertEqual(modification_times, {path: path.stat().st_mtime_ns for path in first})
        self.assertEqual(sources, {path: path.read_bytes() for path in sources})
        self.assertEqual(len(self.names), validate_solution(self.solution)["valid"])
        self.assertEqual(len(self.names), inspect_solution(self.solution)["existingXdrDetectionCount"])
        self.assertEqual(self.names, [item["detection"] for item in runtime_validation_plan(self.solution)["rules"]])
        html = Path(result["transformationReport"]).read_text()
        self.assertIn("XDR Detections/Execution/Deep/Rule.yml", html)
        self.assertEqual(len(self.names), len(list(self.output.rglob("*.*"))))

    def test_nested_reconversion_requires_overwrite_and_preserves_release(self) -> None:
        convert_solution(self.solution)
        target = self.output / "Execution/Deep/Rule.yml"
        document = yaml.safe_load(target.read_text())
        document["version"] = "3.7.4"
        target.write_text(yaml.safe_dump(document, sort_keys=False))
        source = self.analytic / "Execution/Deep/Rule.yml"
        source.write_text(source.read_text().replace("version: 1.0.0", "version: 1.0.3"))
        before = target.read_bytes()
        self.assertEqual(1, convert_solution(self.solution)["conflicts"])
        self.assertEqual(before, target.read_bytes())
        self.assertEqual(0, convert_solution(self.solution, overwrite=True)["conflicts"])
        updated = yaml.safe_load(target.read_text())
        self.assertEqual("3.7.4", updated["version"])
        self.assertEqual("1.0.3", updated["contentProvenance"]["source"]["version"])
        self.assertEqual(document["properties"]["id"], updated["properties"]["id"])

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
    def test_powershell_packager_resolves_nested_manifest_references(self) -> None:
        result = convert_solution(self.solution)
        helper = Path(__file__).resolve().parents[2] / "Create-Azure-Sentinel-Solution/common/customDetections.ps1"
        references = [item["outputRelativePath"] for item in result["results"]]
        repository = str(self.solution.parent.parent).replace("'", "''")
        helper_reference = str(helper).replace("'", "''")
        statements = [
            "Resolve-CustomDetectionPath "
            f"-RepositoryRoot '{repository}' "
            "-SolutionName 'Nested' "
            f"-ConfiguredPath '{reference}'"
            for reference in references + [value.replace("/", "\\") for value in references]
        ]
        command = (
            f". '{helper_reference}'; @("
            + "; ".join(statements) + ") | ConvertTo-Json -Compress"
        )
        completed = subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
            check=True, capture_output=True, text=True,
        )
        resolved = [Path(value).resolve() for value in json.loads(completed.stdout)]
        expected = xdr_detection_files(self.output)
        self.assertEqual(expected + expected, resolved)

    def test_legacy_flat_output_requires_manual_reconciliation_even_with_overwrite(self) -> None:
        convert_solution(self.solution)
        nested = self.output / "Execution/Deep/Rule.yml"
        legacy = self.output / "Rule.yml"
        nested.rename(legacy)
        before = legacy.read_bytes()
        for overwrite in (False, True):
            result = convert_solution(self.solution, overwrite=overwrite)
            self.assertEqual(1, result["conflicts"])
            self.assertIn("explicitly relocate", next(
                item for item in result["results"] if item["status"] == "conflict"
            )["errors"][0])
            self.assertFalse(nested.exists())
            self.assertEqual(before, legacy.read_bytes())

    def test_unidentified_flat_output_is_not_duplicated(self) -> None:
        self.output.mkdir()
        flat = self.output / "Rule.yml"
        flat.write_text("manual: content\n")
        self.assertEqual(1, convert_solution(self.solution, overwrite=True)["conflicts"])
        self.assertEqual("manual: content\n", flat.read_text())
        self.assertFalse((self.output / "Execution/Deep/Rule.yml").exists())

    def test_legacy_source_alias_and_config_exclusion(self) -> None:
        self.analytic.rename(self.solution / "Analytics Rules")
        self.assertEqual(len(self.names), convert_solution(self.solution)["converted"])
        nested = self.output / "Execution/Deep"
        (nested / "migration-config.yaml").write_text("rules: {}\n")
        (nested / "migration-config.yml").write_text("rules: {}\n")
        (nested / "manifest.json").write_text("{}")
        self.assertEqual(len(self.names), validate_solution(self.solution)["valid"])
        for path in xdr_detection_files(self.output):
            self.assertTrue(yaml.safe_load(path.read_text())["contentProvenance"]["source"]["path"].startswith("Analytics Rules/"))

    def test_recursive_runtime_and_report_do_not_conflate_same_basenames(self) -> None:
        convert_solution(self.solution)
        query_hashes = {
            item["detection"]: item["sentinelQuerySha256"]
            for item in runtime_validation_plan(self.solution)["rules"]
        }
        entries = [
            {
                "detection": name, "status": "passed", "rowCount": index,
                "querySha256": query_hashes[name],
            }
            for index, name in enumerate(self.names)
        ]
        entries[0].update(status="blocked", error="specific nested failure")
        results = Path(self.temp.name) / "runtime.json"
        results.write_text(json.dumps({"results": entries}))
        recorded = record_runtime_validation(self.solution, provider="triage-mcp", results_path=results)
        self.assertEqual(len(self.names), recorded["total"])
        report = build_solution_report(self.solution)
        self.assertEqual(len(self.names), report["summary"]["rules"])
        for index, item in enumerate(report["rules"]):
            self.assertEqual("converted", item["customDetection"]["conversionStatus"])
            runtime = item["analyticRule"]["runtime"]
            self.assertEqual(index, runtime[0]["rowCount"])
            self.assertEqual("blocked" if index == 0 else "passed", runtime[0]["status"])
        entries[0]["detection"] = "Rule.yml"
        results.write_text(json.dumps(entries))
        with self.assertRaisesRegex(ValueError, "missing detections"):
            record_runtime_validation(self.solution, provider="triage-mcp", results_path=results)

    def test_legacy_absolute_manifest_still_maps_distinct_nested_sources(self) -> None:
        result = convert_solution(self.solution)
        manifest = Path(result["manifest"])
        for item in result["results"]:
            item.pop("sourceRelativePath")
            item.pop("outputRelativePath")
        manifest.write_text(json.dumps(result))
        self.assertEqual(
            ["converted"] * len(self.names),
            [item["customDetection"]["conversionStatus"] for item in build_solution_report(self.solution)["rules"]],
        )

    @mock.patch("sentinel_xdr_migration.runtime._advanced_hunting_token", return_value="test")
    @mock.patch("sentinel_xdr_migration.runtime.run_advanced_hunting_query")
    def test_graph_runtime_covers_nested_files(self, query, token) -> None:
        convert_solution(self.solution)
        query.return_value = {
            "ok": True, "statusCode": 200, "rowCount": 0,
            "schema": [], "error": None, "errorDetails": None,
        }
        result = validate_advanced_hunting(self.solution)
        self.assertEqual(self.names, [item["detection"] for item in result["results"]])

    def test_parity_uses_relative_paths_and_rejects_ambiguous_stems(self) -> None:
        convert_solution(self.solution)
        _, pairs = _load_pairs(self.solution)
        self.assertEqual(self.names, [item["detection"] for item in pairs])
        _, selected = _load_pairs(self.solution, ["Execution\\SampleRule.yaml"])
        self.assertEqual("Execution/SampleRule.yaml", selected[0]["detection"])
        with self.assertRaisesRegex(ValueError, "ambiguous detection"):
            _load_pairs(self.solution, ["SampleRule"])
        self.assertEqual("Execution/Deep/Rule.yml", detection_reference("Rule", self.names))
        plan = Path(self.temp.name) / "plan.json"
        plan.write_text(json.dumps({"fixtures": [{"detection": "SampleRule"}]}))
        with mock.patch("sentinel_xdr_migration.alert_parity.require_locked_target", return_value={"workspaceResourceId": "test"}):
            with self.assertRaisesRegex(ValueError, "ambiguous detection"):
                start_alert_parity_batch(self.solution, plan_path=plan)

    def test_mocked_deployment_covers_all_nested_ars_and_cds(self) -> None:
        convert_solution(self.solution)
        (self.solution / "Data").mkdir(exist_ok=True)
        (self.solution / "Data/Solution_Nested.json").write_text(json.dumps({
            "Version": "3.1.0", "Metadata": "SolutionMetadata.json",
        }))
        (self.solution / "SolutionMetadata.json").write_text(json.dumps({
            "publisherId": "testpublisher", "offerId": "nested",
        }))
        with (
            mock.patch("sentinel_xdr_migration.analytic_deployment.require_locked_target", return_value={"workspaceResourceId": "test"}),
            mock.patch("sentinel_xdr_migration.analytic_deployment._arm_token", return_value="test"),
            mock.patch("sentinel_xdr_migration.analytic_deployment._arm_request", return_value=(201, {"properties": {"enabled": False}})) as arm,
        ):
            result = deploy_analytic_rules(self.solution)
        self.assertEqual(len(self.names), result["succeeded"])
        self.assertEqual(len(self.names), arm.call_count)
        stored = {}

        def graph_request(method, url, token, payload=None):
            if method == "PATCH":
                stored[url] = payload
            return 200, {"status": "disabled", **stored.get(url, {})}

        with (
            mock.patch("sentinel_xdr_migration.deployment.require_locked_target", return_value={"tenantId": "test"}),
            mock.patch("sentinel_xdr_migration.deployment._deployment_token", return_value="test"),
            mock.patch("sentinel_xdr_migration.deployment._graph_request", side_effect=graph_request),
        ):
            result = deploy_solution(self.solution)
        self.assertEqual(len(self.names), result["succeeded"])
        self.assertEqual(len(self.names), len({item["file"] for item in result["results"]}))

    def test_escaping_paths_and_symlinks_are_rejected(self) -> None:
        for name in ("../outside.yaml", "/outside.yaml", r"C:\outside.yaml", r"..\outside.yaml"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                content_path(self.output, name)
        external = Path(self.temp.name) / "outside"
        external.mkdir()
        linked = self.analytic / "linked"
        linked.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "escapes|symlink"):
            inspect_solution(self.solution)
        linked.unlink()
        self.output.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            convert_solution(self.solution)
        self.assertEqual([], list(external.iterdir()))

    def test_runtime_provenance_cannot_escape_solution(self) -> None:
        convert_solution(self.solution)
        target = self.output / self.names[0]
        document = yaml.safe_load(target.read_text())
        document["contentProvenance"]["source"]["path"] = "../outside.yaml"
        target.write_text(yaml.safe_dump(document))
        with self.assertRaisesRegex(ValueError, "relative and contained"):
            runtime_validation_plan(self.solution)


if __name__ == "__main__":
    unittest.main()
