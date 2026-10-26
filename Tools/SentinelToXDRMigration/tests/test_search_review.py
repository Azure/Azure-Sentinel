from __future__ import annotations

import io
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from sentinel_xdr_migration.converter import build_xdr_document, convert_query


SEARCH_REASON = "search queries should be replaced with explicit tables"
REPOSITORY = Path(__file__).resolve().parents[3]


class SearchReviewTests(unittest.TestCase):
    def test_comments_literals_and_identifiers_do_not_request_search_review(self):
        queries = [
            '// search *\nDeviceEvents | count',
            'DeviceEvents // | search "needle"',
            '/* search *\n| search "needle" */ DeviceEvents | count',
            'DeviceEvents | where ActionType == "search"',
            "DeviceEvents | where ActionType == 'search'",
            'DeviceEvents | extend Message="http://example/search /* search */"',
            r'''DeviceEvents | extend Message="escaped \" search // text"''',
            r"""DeviceEvents | extend Message='escaped \' search /* text'""",
            'DeviceEvents | extend Message=@"quote "" search // text"',
            "DeviceEvents | extend Message=@'quote '' search /* text'",
            'DeviceEvents | extend Message=```multiline\n" search // text\n```',
            'DeviceEvents | extend Message=h"search"',
            'DeviceEvents | project search, SearchResult',
            'DeviceEvents | extend search=ActionType | where search == "needle"',
            'DeviceEvents | extend Alias=search | project Alias',
            'DeviceEvents | where (search == "needle")',
            'DeviceEvents | where (search has "needle")',
            'DeviceEvents | extend Found=search contains "needle"',
            'DeviceEvents | where (search and Enabled)',
            "DeviceEvents | project ['search']",
            'DeviceEvents | where Fields.search == "needle"',
            'let search = DeviceEvents; search | count',
            'let Alias = search; Alias | count',
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertNotIn(SEARCH_REASON, convert_query(query, {})[1])

    def test_executable_search_still_requests_review(self):
        queries = [
            'search "needle"',
            'SEARCH kind=case_sensitive "needle"',
            'search in (DeviceEvents) "needle"',
            'search *',
            'search ActionType == "needle"',
            'search ActionType has "needle"',
            'DeviceEvents | search "needle"',
            'DeviceEvents | search (ActionType == "needle")',
            'let Events = search "needle"; Events | count',
            'let Events = (search "needle"); Events | count',
            'let Events = () { search "needle" }; Events()',
            'union (search "needle"), DeviceEvents',
            'DeviceEvents | join (search "needle") on DeviceId',
            '/* search in a comment */ search "needle"',
            'DeviceEvents | /* multiline\ncomment */ search /* predicate */ "needle"',
            'DeviceEvents // search in comment\n| search "needle"',
            'DeviceEvents | extend Message="https://example" | search "needle"',
            'DeviceEvents | extend Message="/* not a comment" | search "needle"',
            r'''DeviceEvents | extend Message=@"C:\" | search "needle"''',
            r"""DeviceEvents | extend Message=@'C:\' | search "needle" """,
            'DeviceEvents | extend Message=```" // multiline\n``` | search "needle"',
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(1, convert_query(query, {})[1].count(SEARCH_REASON))

    def test_actual_c2_namedpipe_comment_is_not_an_operator(self):
        source = REPOSITORY / (
            "Solutions/Microsoft Defender XDR/Analytic Rules/"
            "Command and Control/C2-NamedPipe.yaml"
        )
        query = yaml.safe_load(source.read_text(encoding="utf-8"))["query"]
        self.assertIn("search uses has_any", query.splitlines()[0])
        self.assertTrue(query.splitlines()[0].lstrip().startswith("//"))
        self.assertIn("| where ParsedFields.PipeName has_any (badPipeNames)", query)
        self.assertNotIn(SEARCH_REASON, convert_query(query, {})[1])

    def test_document_review_gate_distinguishes_comment_from_operator(self):
        root = Path("search-review-fixture")
        rule = {
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "Search review fixture",
            "queryFrequency": "1h",
            "queryPeriod": "4h",
            "entityMappings": [{
                "entityType": "Host",
                "fieldMappings": [{"identifier": "DeviceId", "columnName": "DeviceId"}],
            }],
        }
        for query, needs_review in (
            ('// search "needle"\nDeviceEvents', False),
            ('DeviceEvents | search "needle"', True),
        ):
            with self.subTest(query=query):
                rule["query"] = query
                original_open = Path.open

                def open_input(path, *args, **kwargs):
                    expected_path = root / "Analytic Rules/Rule.yaml"
                    if path == expected_path:
                        return io.StringIO(yaml.safe_dump(rule))
                    return original_open(path, *args, **kwargs)

                with patch.object(Path, "open", autospec=True, side_effect=open_input), \
                     patch("sentinel_xdr_migration.converter.normalize_parser_bindings",
                           side_effect=lambda text, _: (text, [])):
                    document = build_xdr_document(root / "Analytic Rules/Rule.yaml", root, {})
                conversion = document["contentProvenance"]["conversion"]
                self.assertEqual(needs_review, conversion["reviewRequired"])
                self.assertEqual("needsReview" if needs_review else "converted", conversion["status"])
                self.assertEqual([SEARCH_REASON] if needs_review else [], conversion["reviewReasons"])
                self.assertFalse(conversion["errors"])
                self.assertEqual("disabled", document["properties"]["status"])

    def test_other_kql_gates_are_unchanged(self):
        for query, message, index in (
            ('workspace("other").DeviceEvents', "cross-workspace queries require manual redesign", 2),
            ('externaldata(Value:string) ["https://example"]',
             "externaldata availability must be verified by runtime validation", 1),
            ('union isfuzzy=true DeviceEvents, DeviceInfo',
             "isfuzzy unions can still fail semantic binding in Advanced Hunting", 1),
            ('_Im_Test()', "ASIM parser availability must be verified in Advanced Hunting", 1),
        ):
            with self.subTest(query=query):
                self.assertIn(message, convert_query(query, {})[index])


if __name__ == "__main__":
    unittest.main()
