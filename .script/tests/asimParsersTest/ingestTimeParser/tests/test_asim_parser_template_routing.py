import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "asim_parser_file_utils.py"
)
SPEC = importlib.util.spec_from_file_location(
    "asim_parser_file_utils", MODULE_PATH
)
PARSER_FILE_UTILS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARSER_FILE_UTILS)


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

    def test_selects_each_source_without_overwriting_the_shared_fixture(self):
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
                    self.assertEqual(self.resolve(query), fixtures[source])
        self.assertEqual(legacy.read_bytes(), legacy_contents)

    def test_source_specific_fixture_does_not_require_a_legacy_fixture(self):
        source = "ProofPointTAPClicksBlockedV2_CL"
        selected = self.fixture(source)
        self.assertEqual(self.resolve(f"{source} | where true"), selected)

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

    def test_missing_source_specific_and_legacy_fixtures_fail_explicitly(self):
        with self.assertRaises(FileNotFoundError):
            self.resolve("ProofPointTAPClicksBlockedV2_CL | where true")
