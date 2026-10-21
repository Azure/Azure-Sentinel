from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml

from solution_manager.migration.converter import build_xdr_document
from solution_manager.migration.parser_inlining import inline_solution_parsers

from test_parser_bindings import rule


class ParserInliningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.solution = Path(self.temp.name) / "Solutions" / "Sample"
        self.parsers = self.solution / "Parsers"
        self.parsers.mkdir(parents=True)
        self.source = self.solution / "Analytic Rules" / "Example.yaml"
        self.source.parent.mkdir()

    def parser(self, name: str, query: str, **extra) -> None:
        (self.parsers / f"{name}.yaml").write_text(yaml.safe_dump({
            "FunctionName": name, "FunctionAlias": name, "FunctionQuery": query, **extra,
        }), encoding="utf-8")

    def test_inlines_view_and_renames_references_with_the_binder(self) -> None:
        self.parser("Qualys", "Qualys_CL\n| extend Qualys = 1\n| project Qualys;\n")
        query = "Qualys | where Qualys == 1 | join (Qualys) on Id // Qualys\n| extend s = 'Qualys'"
        result, records, warnings = inline_solution_parsers(query, self.solution)

        self.assertTrue(result.startswith("let XdrInlineQualys = view() {\nQualys_CL"))
        self.assertIn("project Qualys\n};\nXdrInlineQualys | where Qualys == 1 | join (XdrInlineQualys) on Id // Qualys",
                      result)
        self.assertIn("'Qualys'", result)
        self.assertEqual("Qualys", records[0]["alias"])
        self.assertEqual("XdrInlineQualys", records[0]["inlineName"])
        self.assertEqual(hashlib.sha256(b"Qualys_CL\n| extend Qualys = 1\n| project Qualys").hexdigest(),
                         records[0]["functionQuerySha256"])
        self.assertEqual(1, len(warnings))
        self.assertFalse(result.startswith("let _"))

    def test_parameters_keep_call_syntax_with_defaults(self) -> None:
        self.parser("Param", "T | where a > n and s == name", FunctionParams=[
            {"Name": "n", "Type": "int", "Default": 3},
            {"Name": "name", "Type": "string", "Default": "it's"},
            {"Name": "flag", "Type": "bool", "Default": False},
        ])
        result, _, _ = inline_solution_parsers("Param(5) | take 1", self.solution)
        self.assertIn("let XdrInlineParam = (n:int=3, name:string='it\\'s', flag:bool=false) {", result)
        self.assertTrue(result.endswith("XdrInlineParam(5) | take 1"))

    def test_nested_parsers_are_emitted_in_dependency_order_and_cycles_fail(self) -> None:
        self.parser("Outer", "Inner | extend x = 1")
        self.parser("Inner", "Base_CL")
        result, records, _ = inline_solution_parsers("Outer | take 1", self.solution)
        self.assertEqual(["Inner", "Outer"], [item["alias"] for item in records])
        self.assertLess(result.index("let XdrInlineInner"), result.index("let XdrInlineOuter"))
        self.assertIn("XdrInlineInner | extend x = 1", result)

        self.parser("Inner", "Outer")
        with self.assertRaisesRegex(ValueError, "cycle"):
            inline_solution_parsers("Outer | take 1", self.solution)

    def test_name_collisions_get_digit_suffixes_and_local_shadows_are_untouched(self) -> None:
        self.parser("Qualys", "Qualys_CL")
        result, records, _ = inline_solution_parsers(
            "let XdrInlineQualys = 1; Qualys | extend v = XdrInlineQualys", self.solution)
        self.assertEqual("XdrInlineQualys2", records[0]["inlineName"])
        self.assertIn("Qualys | extend v", result.replace("XdrInlineQualys2 | extend v", "Qualys | extend v"))

        shadow = "let Qualys = datatable(a:int)[1]; Qualys | take 1"
        self.assertEqual((shadow, [], []), inline_solution_parsers(shadow, self.solution))

    def test_opt_out_and_unrelated_queries_are_unchanged(self) -> None:
        self.parser("Qualys", "Qualys_CL")
        query = "Qualys | take 1"
        self.assertEqual((query, [], []), inline_solution_parsers(query, self.solution, {"inlineSolutionParsers": False}))
        self.assertEqual(("Other | take 1", [], []), inline_solution_parsers("Other | take 1", self.solution))
        with self.assertRaises(ValueError):
            inline_solution_parsers(query, self.solution, {"inlineSolutionParsers": "no"})

    def test_converter_inlines_by_default_records_provenance_and_keeps_source_hash(self) -> None:
        self.parser("Qualys", "CommonSecurityLog | extend Ring0SourceIp = tostring(SourceIP)")
        source_query = "Qualys | where Ring0SourceIp != ''"
        self.source.write_text(yaml.safe_dump(rule(source_query)), encoding="utf-8")

        document = build_xdr_document(self.source, self.solution, {})
        text = document["properties"]["queryCondition"]["queryText"]
        conversion = document["contentProvenance"]["conversion"]
        self.assertTrue(text.startswith("let XdrInlineQualys = view() {"))
        self.assertTrue(text.endswith("XdrInlineQualys | where Ring0SourceIp != ''"))
        self.assertEqual("Qualys", conversion["inlinedParsers"][0]["alias"])
        self.assertEqual(hashlib.sha256(source_query.encode()).hexdigest(),
                         document["contentProvenance"]["source"]["querySha256"])
        flat = [table for item in document["contentProvenance"]["requiredWorkloads"] for table in item["dataTypes"]]
        self.assertIn("CommonSecurityLog", flat)
        self.assertNotIn("Qualys", flat)

        self.parser("Fuzzy", "union isfuzzy=true CommonSecurityLog, Syslog")
        self.source.write_text(yaml.safe_dump(rule("Fuzzy | take 1")), encoding="utf-8")
        fuzzy = build_xdr_document(self.source, self.solution, {})
        conversion = fuzzy["contentProvenance"]["conversion"]
        self.assertEqual([], conversion["reviewReasons"])
        self.assertTrue(any("isfuzzy" in note for note in conversion["warnings"]))
        self.source.write_text(yaml.safe_dump(rule("union isfuzzy=true CommonSecurityLog, Syslog")), encoding="utf-8")
        authored = build_xdr_document(self.source, self.solution, {})
        self.assertTrue(any("isfuzzy" in reason for reason in authored["contentProvenance"]["conversion"]["reviewReasons"]))
        self.source.write_text(yaml.safe_dump(rule(source_query)), encoding="utf-8")

        opted_out = build_xdr_document(self.source, self.solution, {"inlineSolutionParsers": False})
        self.assertEqual(source_query, opted_out["properties"]["queryCondition"]["queryText"])
        self.assertNotIn("inlinedParsers", opted_out["contentProvenance"]["conversion"])


if __name__ == "__main__":
    unittest.main()
