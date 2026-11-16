import ast
import csv
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
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


class ParentParserRoutingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def write_parser(self, name, children=(), **properties):
        document = {
            "ParserName": name,
            "EquivalentBuiltInParser": "_" + name,
            "Normalization": {"Schema": "AuditEvent"},
            "ParserQuery": "union " + ", ".join(child + "()" for child in children),
            "Parsers": ["_" + child for child in children],
            **properties,
        }
        path = self.directory / (name + ".yaml")
        path.write_text(TEMPLATE_VERIFIER.yaml.safe_dump(document), encoding="utf-8")
        return document, path

    def resolve(self, parser, path, file_type="ASim"):
        return TEMPLATE_VERIFIER.get_parent_parser(
            parser, str(path), "AuditEvent", file_type
        )

    def test_missing_null_and_empty_parent_keep_schema_unifier_defaults(self):
        for file_type, prefix, root in (
            ("ASim", "ASim", "ASimAuditEvent"),
            ("vim", "vim", "imAuditEvent"),
        ):
            child_name = prefix + "AuditEventContoso"
            self.write_parser(root, [child_name])
            for properties in ({}, {"ParentParser": None}, {"ParentParser": ""}):
                with self.subTest(file_type=file_type, properties=properties):
                    parser, path = self.write_parser(child_name, **properties)
                    parent, _ = self.resolve(parser, path, file_type)
                    self.assertEqual(parent["ParserName"], root)

    def test_explicit_parent_resolves_each_variant_and_checks_ancestors(self):
        for file_type, prefix, root in (
            ("ASim", "ASim", "ASimAuditEvent"),
            ("vim", "vim", "imAuditEvent"),
        ):
            with self.subTest(file_type=file_type):
                parent_name = prefix + "AuditEventContoso"
                child_name = parent_name + "Child"
                self.write_parser(root, [parent_name])
                self.write_parser(parent_name, [child_name])
                parser, path = self.write_parser(child_name, ParentParser=parent_name)
                parent, _ = self.resolve(parser, path, file_type)
                self.assertEqual(parent["ParserName"], parent_name)
                self.write_parser(root)
                with self.assertRaisesRegex(ValueError, "must be registered"):
                    self.resolve(parser, path, file_type)

    def test_invalid_missing_mismatched_and_cross_schema_parents_fail(self):
        name = "ASimAuditEventContosoChild"
        for parent_name in ("../outside", "vimAuditEventContoso", 42, []):
            with self.subTest(parent_name=parent_name):
                parser, path = self.write_parser(name, ParentParser=parent_name)
                with self.assertRaises(ValueError):
                    self.resolve(parser, path)
        parent_name = "ASimAuditEventContoso"
        parser, path = self.write_parser(name, ParentParser=parent_name)
        with patch.object(TEMPLATE_VERIFIER, "read_local_yaml", return_value=None):
            with self.assertRaisesRegex(ValueError, "missing"):
                self.resolve(parser, path)
        self.write_parser(parent_name, [name], ParserName="ASimAuditEventWrong")
        with self.assertRaisesRegex(ValueError, "mismatched ParserName"):
            self.resolve(parser, path)
        self.write_parser(parent_name, [name], Normalization={"Schema": "Dns"})
        with self.assertRaisesRegex(ValueError, "must use schema"):
            self.resolve(parser, path)

    def test_self_parent_and_indirect_cycles_fail(self):
        name = "ASimAuditEventContosoChild"
        parser, path = self.write_parser(name, [name], ParentParser=name)
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.resolve(parser, path)
        parent_name = "ASimAuditEventContoso"
        parser, path = self.write_parser(name, [parent_name], ParentParser=parent_name)
        self.write_parser(parent_name, [name], ParentParser=name)
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.resolve(parser, path)

    def test_both_membership_checks_remain_required(self):
        name = "ASimAuditEventContoso"
        parser, path = self.write_parser(name, ParentParser="ASimAuditEvent")
        for properties in (
            {"ParserQuery": name + "Other()"},
            {"Parsers": []},
        ):
            with self.subTest(properties=properties):
                self.write_parser("ASimAuditEvent", [name], **properties)
                with self.assertRaisesRegex(ValueError, "must be registered"):
                    self.resolve(parser, path)

    def test_current_aws_cloudtrail_templates_pass_without_exclusions(self):
        root = MODULE_PATH.parents[3]
        parsers = root / "Parsers" / "ASimAuditEvent" / "Parsers"
        sample_dir = root / "Sample Data" / "ASIM"
        if (
            not any(parsers.glob("ASimAuditEventAWSCloudTrailEC2*.yaml"))
            or not (sample_dir / "AWS_CloudTrail_AuditEvent_IngestedLogs.csv").is_file()
        ):
            self.skipTest("AWSCloudTrail EC2 companion parsers and sample fixture are required.")
        paths = sorted(parsers.glob("*AWSCloudTrail*.yaml"))
        for path in paths:
            with self.subTest(parser=path.name):
                parser = TEMPLATE_VERIFIER.yaml.safe_load(path.read_text(encoding="utf-8"))
                file_type = "vim" if path.name.startswith("vim") else "ASim"
                parent, _ = self.resolve(parser, path, file_type)
                results = TEMPLATE_VERIFIER.extract_and_check_properties(
                    parser, parent, file_type, str(sample_dir)
                )
                self.assertFalse(
                    [result for result in results if "Fail" in result[-1]],
                    results,
                )

    def test_synthetic_fixture_covers_each_child_without_overlapping_routes(self):
        root = MODULE_PATH.parents[3]
        fixture = root / "Sample Data" / "ASIM" / "AWS_CloudTrail_AuditEvent_IngestedLogs.csv"
        parsers = root / "Parsers" / "ASimAuditEvent" / "Parsers"
        paths = sorted(parsers.glob("ASimAuditEventAWSCloudTrailEC2*.yaml"))
        if not fixture.is_file() or not paths:
            self.skipTest("AWSCloudTrail EC2 companion parsers and sample fixture are required.")
        with fixture.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        catalogs = {}
        for path in paths:
            query = TEMPLATE_VERIFIER.yaml.safe_load(
                path.read_text(encoding="utf-8")
            )["ParserQuery"]
            catalogs[path.stem] = set(re.findall(
                r'^\s*"([^"]+)", "[^"]+", "[^"]+"', query, re.MULTILINE
            ))
        self.assertEqual(len(rows), 2 * len(catalogs))
        self.assertEqual(len({row["AwsEventId"] for row in rows}), len(rows))
        for name, events in catalogs.items():
            matching = [row for row in rows if row["EventName"] in events]
            self.assertEqual(len(matching), 2, name)
            self.assertEqual({bool(row["ErrorCode"]) for row in matching}, {False, True})
        for row in rows:
            self.assertEqual(row["Type"], "AWSCloudTrail")
            self.assertEqual(row["EventSource"], "ec2.amazonaws.com")
            self.assertEqual(sum(row["EventName"] in events for events in catalogs.values()), 1)
            self.assertTrue(json.loads(row["RequestParameters"]))
            self.assertIsInstance(json.loads(row["ResponseElements"]), dict)


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
                "R100\tParsers/ASimDns/IngestTimeParsers/Old.yaml\t",
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


class SampleFixtureIngestionTests(unittest.TestCase):
    def run_ingestion(self, fixtures, tables, table_type="builtin", upload_results=None):
        script_path = MODULE_PATH.with_name("ingestASimSampleData.py")
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
        initialization = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "ingested_fixtures"
                for target in node.targets
            )
        )
        ingestion_loop = next(node for node in tree.body if isinstance(node, ast.For))
        code = compile(
            ast.Module(body=[initialization, ingestion_loop], type_ignores=[]),
            str(script_path),
            "exec",
        )
        parser = {
            "ParserQuery": "AWSCloudTrail | where true",
            "Normalization": {"Schema": "AuditEvent"},
            "EquivalentBuiltInParser": "_ASim_AuditEvent_Contoso",
        }

        def open_file(path, mode="r", **kwargs):
            if str(path).endswith(".yaml"):
                return io.StringIO(TEMPLATE_VERIFIER.yaml.safe_dump(parser))
            return io.BytesIO(b"synthetic fixture" if mode == "rb" else b"")

        response = SimpleNamespace(
            status_code=200,
            text=json.dumps({"properties": {"immutableId": "synthetic-dcr"}}),
        )
        namespace = {
            "os": os,
            "json": json,
            "yaml": TEMPLATE_VERIFIER.yaml,
            "current_directory": str(MODULE_PATH.parent),
            "parser_yaml_files": [
                f"Parsers/ASimAuditEvent/Parsers/ASimAuditEventContoso{index}.yaml"
                for index in range(len(fixtures))
            ],
            "extract_schema_name": PARSER_FILE_UTILS.extract_schema_name,
            "is_union_parser": PARSER_FILE_UTILS.is_union_parser,
            "is_empty_parser": PARSER_FILE_UTILS.is_empty_parser,
            "extract_event_vendor_product": Mock(return_value=("AWS", "CloudTrail", "AuditEvent")),
            "resolve_sample_data_path": Mock(side_effect=fixtures),
            "convert_data_csv_to_json": Mock(side_effect=[
                ([{"id": index}], table, []) for index, table in enumerate(tables)
            ]),
            "rebase_time_generated": Mock(side_effect=lambda rows: rows),
            "check_for_custom_table": Mock(return_value=(True, table_type)),
            "get_schema_for_builtin": Mock(return_value=[]),
            "infer_schema_from_data": Mock(return_value=[]),
            "convert_data_type": Mock(side_effect=lambda schema, rows: rows),
            "create_table": Mock(return_value=({}, "table-url", "PUT")),
            "get_table_status": Mock(),
            "create_dcr": Mock(return_value=({}, "dcr-url", "PUT", "synthetic-stream")),
            "hit_api": Mock(return_value=response),
            "senddtosentinel": Mock(
                side_effect=upload_results if upload_results is not None else None,
                return_value=True,
            ),
            "dcr_directory": [],
            "prnumber": "15531",
        }
        with (
            patch("builtins.open", side_effect=open_file),
            patch("sys.stdout", io.StringIO()),
        ):
            exec(code, namespace)
        return namespace

    def test_shared_fixture_is_ingested_once_for_all_changed_parsers(self):
        for table_type in ("builtin", "custom_log"):
            with self.subTest(table_type=table_type):
                fixtures = [Path("fixtures/shared.csv")] * 34
                fixtures[1] = Path("fixtures/subdirectory/../shared.csv")
                result = self.run_ingestion(
                    fixtures, ["Synthetic_CL"] * len(fixtures), table_type
                )
                result["senddtosentinel"].assert_called_once()
                result["create_dcr"].assert_called_once()
                result["rebase_time_generated"].assert_called_once()

    def test_distinct_fixtures_and_destinations_are_not_deduplicated(self):
        for fixtures, tables in (
            ([Path("fixtures/first.csv"), Path("fixtures/second.csv")],
             ["Synthetic_CL", "Synthetic_CL"]),
            ([Path("fixtures/shared.csv")] * 2,
             ["First_CL", "Second_CL"]),
        ):
            for table_type in ("builtin", "custom_log"):
                with self.subTest(fixtures=fixtures, tables=tables, table_type=table_type):
                    result = self.run_ingestion(fixtures, tables, table_type)
                    self.assertEqual(result["senddtosentinel"].call_count, 2)
                    self.assertEqual(result["create_dcr"].call_count, 2)

    def test_failed_upload_does_not_mark_fixture_as_ingested(self):
        for table_type in ("builtin", "custom_log"):
            with self.subTest(table_type=table_type):
                result = self.run_ingestion(
                    [Path("fixtures/shared.csv")] * 3,
                    ["Synthetic_CL"] * 3,
                    table_type,
                    upload_results=[False, True],
                )
                self.assertEqual(result["senddtosentinel"].call_count, 2)
                self.assertEqual(result["create_dcr"].call_count, 2)


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
            MODULE_PATH.parents[3]
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
