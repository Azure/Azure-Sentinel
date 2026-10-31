import importlib.util
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
