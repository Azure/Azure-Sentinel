import ast
import csv
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "asim_parser_file_utils.py"
)
SPEC = importlib.util.spec_from_file_location(
    "asim_parser_file_utils", MODULE_PATH
)
PARSER_FILE_UTILS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARSER_FILE_UTILS)

TEMPLATE_SPEC = importlib.util.spec_from_file_location(
    "asim_parser_template_verifier",
    MODULE_PATH.with_name("VerifyASimParserTemplate.py"),
)
TEMPLATE_VERIFIER = importlib.util.module_from_spec(TEMPLATE_SPEC)
TEMPLATE_SPEC.loader.exec_module(TEMPLATE_VERIFIER)

FILTERING_SPEC = importlib.util.spec_from_file_location(
    "asim_filtering_routing",
    MODULE_PATH.with_name("ASimFilteringTest.py"),
)
FILTERING_VALIDATOR = importlib.util.module_from_spec(FILTERING_SPEC)
FILTERING_SPEC.loader.exec_module(FILTERING_VALIDATOR)


class QueryTimeParserFileSelectionTests(unittest.TestCase):
    def test_mixed_changes_select_only_query_time_parser_files(self):
        changed_files = [
            "Parsers/ASimEmailEvent/Parsers/ASimEmailEventContoso.yaml",
            "Parsers/ASimEmailEvent/IngestTimeParsers/" +
            "ASimEmailEventProofpointPODMailLog.yaml",
            "Parsers/ASimEmailEvent/IngestTimeParsers/notes.txt",
        ]

        self.assertEqual(
            PARSER_FILE_UTILS.filter_query_time_parser_files(changed_files),
            ["Parsers/ASimEmailEvent/Parsers/ASimEmailEventContoso.yaml"],
        )

    def test_ingestion_time_parser_only_changes_select_no_files(self):
        changed_files = [
            "Parsers\\ASimEmailEvent\\IngestTimeParsers\\" +
            "ASimEmailEventProofpointPODMailLog.yaml",
        ]

        self.assertEqual(
            PARSER_FILE_UTILS.filter_query_time_parser_files(changed_files),
            [],
        )

    def test_query_time_parser_changes_remain_selected(self):
        changed_files = [
            "Parsers/ASimDns/Parsers/ASimDnsContoso.yaml",
            "Parsers/ASimDns/Parsers/vimDnsContoso.yaml",
            "Parsers/ASimDns/Parsers/ASimDnsContoso.yml",
        ]

        self.assertEqual(
            PARSER_FILE_UTILS.filter_query_time_parser_files(changed_files),
            [
                "Parsers/ASimDns/Parsers/ASimDnsContoso.yaml",
                "Parsers/ASimDns/Parsers/vimDnsContoso.yaml",
            ],
        )


class QueryTimeParserExecutionRoutingTests(unittest.TestCase):
    query_time_files = [
        "Parsers/ASimDns/Parsers/ASimDnsContoso.yaml",
        "Parsers/ASimDns/Parsers/vimDnsContoso.yaml",
        "Parsers\\ASimDns\\Parsers\\ASimDnsWindows.yaml",
        "Parsers/ASimDns/Parsers/ASimDnsIngestTimeParsersContoso.yaml",
        "Parsers/ASimDns/IngestTimeParsersArchive/ASimDnsContoso.yaml",
    ]
    ingestion_time_files = [
        "Parsers/ASimDns/IngestTimeParsers/ASimDnsContoso.yaml",
        "Parsers\\ASimEmailEvent\\IngestTimeParsers\\ASimEmailEventContoso.yaml",
        "Parsers/ASimAuditEvent/IngestTimeParsers/Nested/ASimAuditEventContoso.yaml",
    ]
    selection_cases = [
        (
            query_time_files + ingestion_time_files + [
                "Parsers/ASimDns/Parsers/notes.txt",
                "Parsers/ASimDns/Parsers/ASimDnsContoso.yml",
            ],
            query_time_files,
        ),
        (ingestion_time_files, []),
        (query_time_files, query_time_files),
    ]

    def test_sample_ingestion_selects_only_query_time_parsers(self):
        script_path = MODULE_PATH.with_name("ingestASimSampleData.py")
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
        selection = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "parser_yaml_files"
                for target in node.targets
            )
        )
        helper_aliases = [
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "filter_query_time_parser_files"
                for target in node.targets
            )
        ]
        code = compile(
            ast.Module(body=helper_aliases + [selection], type_ignores=[]),
            str(script_path),
            "exec",
        )
        for changed_files, expected in self.selection_cases:
            with self.subTest(changed_files=changed_files):
                namespace = {
                    "modified_files": changed_files,
                    "parser_file_utils": PARSER_FILE_UTILS,
                }
                exec(code, namespace)
                self.assertEqual(namespace["parser_yaml_files"], expected)

    def test_filtering_main_selects_only_query_time_parsers(self):
        for changed_files, expected in self.selection_cases:
            with self.subTest(changed_files=changed_files):
                git_results = [
                    SimpleNamespace(stdout="upstream\n"),
                    SimpleNamespace(stdout=""),
                    SimpleNamespace(stdout="\n".join(changed_files)),
                ]
                with (
                    patch.object(FILTERING_VALIDATOR, "attempt_to_connect"),
                    patch.object(
                        FILTERING_VALIDATOR.subprocess, "run",
                        side_effect=git_results,
                    ),
                    patch.object(FILTERING_VALIDATOR, "FilteringTest") as test,
                    patch.object(FILTERING_VALIDATOR.unittest, "TestSuite"),
                    patch.object(
                        FILTERING_VALIDATOR.unittest, "TextTestRunner",
                    ) as runner,
                    patch.object(FILTERING_VALIDATOR.sys, "stdout", io.StringIO()),
                ):
                    runner.return_value.run.return_value.wasSuccessful.return_value = True
                    FILTERING_VALIDATOR.main()
                self.assertEqual(
                    [call.args[1] for call in test.call_args_list],
                    expected,
                )

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
    def test_workflow_schema_data_runner_selects_only_query_time_parsers(self):
        repo_root = MODULE_PATH.parents[3]
        workflow_path = (
            repo_root / ".github" / "workflows" / "runAsimSchemaAndDataTesters.yaml"
        )
        workflow = TEMPLATE_VERIFIER.yaml.safe_load(
            workflow_path.read_text(encoding="utf-8")
        )
        script_step = next(
            step
            for step in workflow["jobs"]["Run-ASim-Schema-Data-tests"]["steps"]
            if "inlineScript" in step.get("with", {})
        )
        self.assertIn(
            '.script/tests/asimParsersTest/runAsimTesters.ps1',
            script_step["with"]["inlineScript"],
        )
        self.assertIn("& $filePath", script_step["with"]["inlineScript"])
        script_path = str(MODULE_PATH.with_name("runAsimTesters.ps1")).replace("'", "''")
        command = r"""
$ErrorActionPreference = 'Stop'
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    '__SCRIPT_PATH__', [ref]$tokens, [ref]$errors
)
if ($errors.Count) { throw ($errors | Out-String) }
$runFunction = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $node.Name -eq 'run'
}, $true)
Invoke-Expression $runFunction.Extent.Text
$global:statusLines = @([Console]::In.ReadToEnd() | ConvertFrom-Json)
$global:selected = @()
$global:testErrors = @()
function Invoke-Expression([string]$Command) {
    if ($Command -eq 'git remote') { return 'upstream' }
    if ($Command -eq 'git fetch upstream') { return }
    if ($Command.StartsWith('git diff --name-status ')) {
        return $global:statusLines
    }
    throw "Unexpected command: $Command"
}
function testSchema([string]$ParserFile) {
    $global:selected += $ParserFile
}
run
[Console]::Out.WriteLine(
    'SELECTED_JSON=' + (ConvertTo-Json -InputObject @($global:selected) -Compress)
)
""".replace("__SCRIPT_PATH__", script_path)
        status_cases = [
            ([f"M\t{path}" for path in changed], expected)
            for changed, expected in self.selection_cases
        ]
        status_cases.append((
            [
                "R100\tParsers/ASimDns/Parsers/Old.yaml\t"
                "Parsers/ASimDns/IngestTimeParsers/New.yaml",
                "R100\tParsers/ASimDns/IngestTimeParsers/Old.yaml\t"
                "Parsers/ASimDns/Parsers/New.yaml",
            ],
            ["Parsers/ASimDns/Parsers/New.yaml"],
        ))
        for statuses, expected in status_cases:
            with self.subTest(statuses=statuses):
                result = subprocess.run(
                    ["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
                    input=json.dumps(statuses),
                    text=True,
                    capture_output=True,
                    check=True,
                )
                selected = next(
                    line.removeprefix("SELECTED_JSON=")
                    for line in result.stdout.splitlines()
                    if line.startswith("SELECTED_JSON=")
                )
                self.assertEqual(json.loads(selected), expected)


class SampleFixtureSelectionTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.sample_dir = Path(temporary_directory.name)

    def fixture(self, table=None, types=None):
        suffix = f"_{table}" if table else ""
        path = self.sample_dir / f"Proofpoint_TAP_EmailEvent{suffix}_IngestedLogs.csv"
        with path.open("w", newline="", encoding="utf-8") as sample_file:
            writer = csv.DictWriter(sample_file, fieldnames=["Type", "id"])
            writer.writeheader()
            for fixture_type in types if types is not None else [table]:
                writer.writerow({"Type": fixture_type, "id": "synthetic-id"})
        return path

    def resolve(self, query):
        return PARSER_FILE_UTILS.resolve_sample_data_path(
            self.sample_dir, "Proofpoint", "TAP", "EmailEvent", query
        )

    def template_results(self):
        parser_dir = (
            Path(__file__).resolve().parents[5]
            / "Parsers" / "ASimEmailEvent" / "Parsers"
        )
        parser = TEMPLATE_VERIFIER.read_local_yaml(
            parser_dir / "ASimEmailEventProofpointTAPClicksPermitted.yaml"
        )
        union = TEMPLATE_VERIFIER.read_local_yaml(parser_dir / "ASimEmailEvent.yaml")
        return TEMPLATE_VERIFIER.extract_and_check_properties(
            parser, union, "ASim", str(self.sample_dir)
        )

    def test_only_switches_the_source_that_mismatches_the_legacy_fixture(self):
        legacy = self.fixture(types=["ProofPointTAPClicksPermittedV2_CL"])
        legacy_contents = legacy.read_bytes()
        sources = [
            "ProofPointTAPClicksBlockedV2_CL",
            "ProofPointTAPClicksPermittedV2_CL",
        ]
        fixtures = {source: self.fixture(source) for source in sources}
        for source in sources:
            for query in (
                f"let parser = () {{\n{source}\n| where true\n}};\nparser()",
                f"let parser = () {{ {source} | where true }}; parser()",
            ):
                with self.subTest(source=source, query=query):
                    expected = (
                        legacy if source == "ProofPointTAPClicksPermittedV2_CL"
                        else fixtures[source]
                    )
                    self.assertEqual(self.resolve(query), expected)
        self.assertEqual(legacy.read_bytes(), legacy_contents)

    def test_matching_legacy_is_kept_even_if_source_specific_data_is_invalid(self):
        source = "ProofPointTAPClicksPermittedV2_CL"
        legacy = self.fixture(types=[source])
        self.fixture(source, types=["Wrong_CL"])
        self.assertEqual(self.resolve(f"{source} | where true"), legacy)

    def test_source_specific_is_used_for_empty_or_mixed_legacy_types(self):
        source = "ProofPointTAPClicksBlockedV2_CL"
        selected = self.fixture(source)
        for types in ([], [""], [source, "Other_CL"]):
            with self.subTest(types=types):
                self.fixture(types=types)
                self.assertEqual(self.resolve(f"{source} | where true"), selected)

    def test_source_specific_fixture_does_not_require_a_legacy_fixture(self):
        source = "ProofPointTAPClicksBlockedV2_CL"
        selected = self.fixture(source)
        self.assertEqual(self.resolve(f"{source} | where true"), selected)

    def test_template_and_ingestion_accept_a_source_specific_only_fixture(self):
        source = "ProofPointTAPClicksPermittedV2_CL"
        selected = self.fixture(source)
        self.assertEqual(self.resolve(f"{source} | where true"), selected)
        self.assertTrue(all(result[2] == "Pass" for result in self.template_results()))

    def test_template_and_ingestion_keep_matching_legacy_data(self):
        source = "ProofPointTAPClicksPermittedV2_CL"
        legacy = self.fixture(types=[source])
        self.fixture(source, types=["Wrong_CL"])
        self.assertEqual(self.resolve(f"{source} | where true"), legacy)
        self.assertTrue(all(result[2] == "Pass" for result in self.template_results()))

    def test_template_reports_fixture_resolution_errors_as_validation_failures(self):
        source = "ProofPointTAPClicksPermittedV2_CL"
        self.fixture(source, types=["Wrong_CL"])
        with self.assertRaises(ValueError):
            self.resolve(f"{source} | where true")
        sample_result = self.template_results()[-1]
        self.assertIn("Fail", sample_result[2])
        self.assertIn("must contain only Type", sample_result[1])

    def test_preserves_legacy_fallback_without_a_matching_source_specific_file(self):
        legacy = self.fixture(types=["ProofPointTAPClicksPermittedV2_CL"])
        self.fixture("ProofPointTAPClicksBlockedV2_CL")
        self.assertEqual(
            self.resolve("ProofPointTAPClicksPermittedV2_CL | where true"),
            legacy,
        )

    def test_does_not_select_fixtures_from_comments_or_string_values(self):
        legacy = self.fixture(types=["Other_CL"])
        self.fixture("ProofPointTAPClicksBlockedV2_CL")
        decoy = "ProofPointTAPClicksBlockedV2_CL | where true"
        for decoration in (
            f"// {decoy}",
            f"/*\n{decoy}\n*/",
            f'let description = "{decoy}";',
            f'let description = @"\n{decoy}\n";',
            f"let description = @'\n{decoy}\n';",
            f"let description = ```\n{decoy}\n```;",
        ):
            with self.subTest(decoration=decoration):
                self.assertEqual(
                    self.resolve(decoration + "\nOther_CL | where true"), legacy
                )

    def test_invalid_source_specific_type_does_not_fall_back_to_legacy(self):
        self.fixture(types=["ProofPointTAPClicksPermittedV2_CL"])
        blocked = "ProofPointTAPClicksBlockedV2_CL"
        for types in (
            ["ProofPointTAPClicksPermittedV2_CL"],
            [blocked, "ProofPointTAPClicksPermittedV2_CL"],
            [],
        ):
            with self.subTest(types=types):
                self.fixture(blocked, types=types)
                with self.assertRaisesRegex(ValueError, "must contain only Type"):
                    self.resolve(f"{blocked} | where true")

    def test_multiple_matching_source_specific_fixtures_are_rejected(self):
        self.fixture(types=["Other_CL"])
        self.fixture("First_CL")
        self.fixture("Second_CL")
        with self.assertRaisesRegex(ValueError, "Multiple source-specific"):
            self.resolve(
                "let first = First_CL | where true;\n"
                "let second = Second_CL | where true;\nfirst"
            )

    def test_union_source_specific_routing_accounts_for_all_operands(self):
        self.fixture(types=["Other_CL"])
        self.fixture("First_CL")
        self.fixture("Second_CL")
        for query in (
            "union isfuzzy=true\nFirst_CL,\nSecond_CL | where true",
            "union isfuzzy=true First_CL, Second_CL | where true",
            "First_CL | union Second_CL | where true",
            "union kind=outer withsource=Source First_CL, Second_CL | where true",
        ):
            with self.subTest(query=query):
                with self.assertRaisesRegex(ValueError, "Multiple source-specific"):
                    self.resolve(query)

    def test_fuzzy_union_with_one_matching_fixture_preserves_legacy_priority(self):
        selected = self.fixture("Second_CL")
        for query in (
            "union isfuzzy=true\nFirst_CL,\nSecond_CL | where true",
            "union isfuzzy=true First_CL, Second_CL | where true",
        ):
            for legacy_type in ("Second_CL", "Other_CL"):
                with self.subTest(query=query, legacy_type=legacy_type):
                    legacy = self.fixture(types=[legacy_type])
                    expected = legacy if legacy_type == "Second_CL" else selected
                    self.assertEqual(self.resolve(query), expected)

    def test_matching_legacy_is_preserved_with_an_unresolved_union(self):
        source = "First_CL"
        legacy = self.fixture(types=[source])
        self.fixture(source)
        query = (
            f"let current = {source} | where true;\n"
            "union current, table('Older_CL') | where true"
        )
        self.assertEqual(self.resolve(query), legacy)

    def test_version_union_keeps_matching_legacy_even_with_multiple_fixtures(self):
        legacy = self.fixture(types=["First_CL"])
        self.fixture("First_CL")
        self.fixture("Second_CL")
        for query in (
            "union isfuzzy=true\nFirst_CL,\nSecond_CL | where true",
            "union isfuzzy=true First_CL, Second_CL | where true",
        ):
            with self.subTest(query=query):
                self.assertEqual(self.resolve(query), legacy)

    def test_unresolved_union_does_not_fall_back_to_an_arbitrary_fixture(self):
        self.fixture(types=["Other_CL"])
        self.fixture("First_CL")
        self.fixture("Second_CL")
        for query in (
            "union First_CL, table('Second_CL') | where true",
            "union hint.spread=2 First_CL, Second_CL | where true",
            "union (First_CL | where true), (Second_CL | where true)",
        ):
            with self.subTest(query=query):
                with self.assertRaisesRegex(
                    ValueError, "Cannot resolve union|Multiple source-specific"
                ):
                    self.resolve(query)

    def test_union_without_source_specific_fixtures_preserves_legacy_behavior(self):
        legacy = self.fixture(types=["First_CL"])
        for query in (
            "union isfuzzy=true First_CL, Second_CL | where true",
            "union First_CL, table('Second_CL') | where true",
        ):
            with self.subTest(query=query):
                self.assertEqual(self.resolve(query), legacy)

    def test_union_of_one_literal_source_retains_matching_legacy_data(self):
        source = "First_CL"
        legacy = self.fixture(types=[source])
        self.fixture(source)
        self.assertEqual(
            self.resolve(f"union isfuzzy=true {source} | where true"), legacy
        )

    def test_missing_source_specific_and_legacy_fixtures_fail_explicitly(self):
        with self.assertRaises(FileNotFoundError):
            self.resolve("ProofPointTAPClicksBlockedV2_CL | where true")
