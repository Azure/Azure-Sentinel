from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.converter import build_xdr_document, convert_query
from sentinel_xdr_migration.parser_bindings import normalize_parser_bindings, solution_parser_names


ROOT = Path(__file__).resolve().parents[1]
HELPERS = ROOT.parent / "Create-Azure-Sentinel-Solution" / "common" / "customDetections.ps1"
FIXTURES = json.loads((ROOT / "tests" / "fixtures" / "parser_collisions.json").read_text())


def rule(query: str) -> dict:
    return {
        "id": "11111111-2222-3333-4444-555555555555",
        "name": "Parser naming regression",
        "version": "1.0.0",
        "queryFrequency": "1h",
        "queryPeriod": "1h",
        "query": query,
        "entityMappings": [{
            "entityType": "IP",
            "fieldMappings": [{"identifier": "Address", "columnName": "Ring0SourceIp"}],
        }],
    }


class ParserBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp.name)
        self.solution = self.repository / "Solutions" / "Sample"
        self.parsers = self.solution / "Parsers"
        self.parsers.mkdir(parents=True)
        self.source = self.solution / "Analytic Rules" / "Example.yaml"
        self.source.parent.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def parser(self, name: str, alias: str | None = None) -> Path:
        path = self.parsers / f"{name}.yaml"
        path.write_text(yaml.safe_dump({
            "FunctionName": name, "FunctionAlias": alias or name,
            "FunctionQuery": "CommonSecurityLog",
        }), encoding="utf-8")
        return path

    def test_discovers_names_aliases_and_nested_yml(self) -> None:
        self.parser("Parser", "Alias")
        nested = self.parsers / "nested"
        nested.mkdir()
        (nested / "Other.yml").write_text("FunctionName: Other\n", encoding="utf-8")
        self.assertEqual(["Alias", "Other", "Parser"], solution_parser_names(self.solution))

    def test_malformed_parser_inventory_is_not_silently_skipped(self) -> None:
        for value in ("- not-an-object\n", "FunctionAlias: 42\n", "FunctionName: ''\n", "{}\n"):
            with self.subTest(value=value):
                (self.parsers / "Bad.yaml").write_text(value)
                with self.assertRaises(ValueError):
                    solution_parser_names(self.solution)

    @mock.patch("sentinel_xdr_migration.parser_bindings.subprocess.run")
    def test_solution_without_parsers_does_not_require_node(self, run: mock.Mock) -> None:
        self.assertEqual(("let Other=1; print Other", []),
                         normalize_parser_bindings("let Other=1; print Other", self.solution))
        run.assert_not_called()

    @mock.patch("sentinel_xdr_migration.parser_bindings.shutil.which", return_value=None)
    def test_missing_node_is_an_explicit_setup_error(self, which: mock.Mock) -> None:
        self.parser("Parser")
        with self.assertRaisesRegex(RuntimeError, "Node.js"):
            normalize_parser_bindings("let Parser=1; print Value=Parser", self.solution)

    def test_converter_normalizes_all_six_queries_and_preserves_sources(self) -> None:
        for fixture in FIXTURES:
            with self.subTest(query=fixture["name"]):
                parser = self.parser(fixture["parser"])
                self.source.write_text(yaml.safe_dump(rule(fixture["query"])), encoding="utf-8")
                before = self.source.read_bytes(), parser.read_bytes()
                document = build_xdr_document(self.source, self.solution, {})
                expected = convert_query(fixture["query"], {})[0].replace(
                    fixture["parser"], f"__xdr_inline_{fixture['parser']}"
                )
                self.assertEqual(expected, document["properties"]["queryCondition"]["queryText"])
                self.assertEqual("disabled", document["properties"]["status"])
                provenance = document["contentProvenance"]
                self.assertEqual(hashlib.sha256(fixture["query"].encode()).hexdigest(),
                                 provenance["source"]["querySha256"])
                self.assertTrue(any("Renamed local parser binding" in warning
                                    for warning in provenance["conversion"]["warnings"]))
                self.assertEqual(before, (self.source.read_bytes(), parser.read_bytes()))

    def test_unsafe_rewrite_blocks_conversion_instead_of_changing_semantics(self) -> None:
        self.parser("Parser")
        query = "let Parser=1; datatable(x:long)[1] | project Parser"
        self.source.write_text(yaml.safe_dump(rule(query)), encoding="utf-8")
        document = build_xdr_document(self.source, self.solution, {})
        self.assertEqual("needsReview", document["contentProvenance"]["conversion"]["status"])
        self.assertTrue(any("output columns" in error
                            for error in document["contentProvenance"]["conversion"]["errors"]))
        self.assertEqual(query, document["properties"]["queryCondition"]["queryText"])

    @unittest.skipUnless(shutil.which("pwsh") and shutil.which("git"), "PowerShell and git are required")
    def test_actual_shared_packager_normalizes_both_faces_without_editing_yaml(self) -> None:
        subprocess.run(["git", "init", "--quiet", str(self.repository)], check=True, capture_output=True)
        output = self.solution / "XDR Detections"
        output.mkdir()
        paths = []
        expected = []
        for index, fixture in enumerate(FIXTURES):
            self.parser(fixture["parser"])
            self.source.write_text(yaml.safe_dump(rule(fixture["query"])), encoding="utf-8")
            document = build_xdr_document(self.source, self.solution, {})
            document["properties"]["id"] = f"parser-test-{index}"
            document["properties"]["queryCondition"]["queryText"] = fixture["query"]
            # Isolate the packaging regression from unrelated conversion review reasons.
            document["contentProvenance"]["conversion"].update(
                status="converted", reviewRequired=False, errors=[], reviewReasons=[]
            )
            path = output / f"Detection{index}.yaml"
            path.write_text(yaml.safe_dump(document), encoding="utf-8")
            paths.append(path)
            properties = copy.deepcopy(document["properties"])
            properties["id"] = f"[if(true(), 'parser-test-{index}', 'parser-test-{index}')]"
            for mappings in properties["detectionAction"]["alertTemplate"]["entityMappings"].values():
                for mapping in mappings:
                    if mapping.get("id"):
                        mapping["id"] = f"[if(true(), '{mapping['id']}', '{mapping['id']}')]"
            properties["queryCondition"]["queryText"] = fixture["query"].replace(
                fixture["parser"], f"__xdr_inline_{fixture['parser']}"
            )
            expected.append(properties)
        native = list(self.parsers.glob("*.yaml")) + paths
        before = {path: path.read_bytes() for path in native}
        content = {
            "Version": "1.0.0",
            "Include XDR Content Registration": True,
            "XDR Detections": [str(path.relative_to(self.solution)) for path in paths],
        }
        script = f"""
$ErrorActionPreference = 'Stop'
$WarningPreference = 'SilentlyContinue'
. '{str(HELPERS).replace("'", "''")}'
$content = [Console]::In.ReadToEnd() | ConvertFrom-Json
$template = [pscustomobject]@{{
    parameters = [pscustomobject]@{{}}
    variables = [pscustomobject]@{{ source = [pscustomobject]@{{
        _analyticRulecontentId1 = '11111111-2222-3333-4444-555555555555'
    }} }}
    resources = @([pscustomobject]@{{
        name = "[variables('source')]"
        properties = [pscustomobject]@{{ contentKind = 'AnalyticsRule' }}
    }})
}}
Add-XdrCustomDetectionsToSolution -SolutionName 'Sample' -ContentToImport $content -Template $template 6>$null | Out-Null
$install = @($template.resources | Where-Object type -eq 'Microsoft.Resources/deployments' |
    ForEach-Object {{ $_.properties.template.resources.detectionRule.properties }})
$registrations = @($template.resources | Where-Object {{ $_.properties.contentKind -eq 'CustomDetection' }} |
    ForEach-Object {{ $_.properties.mainTemplate.resources.detectionRule.properties }})
@{{ install = $install; registrations = $registrations }} | ConvertTo-Json -Depth 100 -Compress
"""
        result = subprocess.run(
            [shutil.which("pwsh"), "-NoProfile", "-NonInteractive", "-Command", script],
            input=json.dumps(content), text=True, encoding="utf-8", capture_output=True,
            cwd=self.repository, timeout=120, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        actual = json.loads(result.stdout)
        self.assertEqual(expected, actual["install"])
        self.assertEqual(expected, actual["registrations"])
        self.assertEqual(before, {path: path.read_bytes() for path in native})


if __name__ == "__main__":
    unittest.main()
