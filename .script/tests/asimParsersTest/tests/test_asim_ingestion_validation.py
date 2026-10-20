import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "asim_ingestion_validation.py"
)
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location(
    "asim_ingestion_validation", MODULE_PATH
)
VALIDATION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATION
SPEC.loader.exec_module(VALIDATION)


TIMESTAMP_1 = "2026-10-19T20:00:00.1234567Z"
TIMESTAMP_2 = "2026-10-19T20:00:01.1234567Z"


def query_table(schema, rows):
    columns = [
        {"name": name, "type": column_type}
        for name, column_type in schema
    ]
    return {
        "columns": columns,
        "rows": [
            [row.get(name) for name, _ in schema]
            for row in rows
        ],
    }


class FakeQueryClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.queries = []

    def query_kql(self, query, *, stage="query"):
        self.queries.append({"stage": stage, "query": query})
        if not self.responses:
            raise AssertionError(f"Unexpected query stage: {stage}")
        expected_stage, response = self.responses.pop(0)
        if stage != expected_stage:
            raise AssertionError(
                f"Expected stage {expected_stage}, received {stage}"
            )
        return response


class QueryConstructionTests(unittest.TestCase):
    def test_builds_exact_filter_query(self):
        query = VALIDATION.build_filter_count_query(
            "Contoso_CL",
            [TIMESTAMP_1, TIMESTAMP_2],
            "source\n| where EventType == 'Login'",
        )

        self.assertIn("let source = materialize(Contoso_CL", query)
        self.assertIn(f"datetime({TIMESTAMP_1})", query)
        self.assertIn("where EventType == 'Login'", query)
        self.assertIn("_AsimSelectedCount=count()", query)

    def test_qtp_query_overrides_disabled_and_pack(self):
        query = VALIDATION.build_query_time_parser_query(
            {
                "ParserParams": [
                    {
                        "Name": "disabled",
                        "Type": "bool",
                        "Default": False,
                    },
                    {
                        "Name": "pack",
                        "Type": "bool",
                        "Default": False,
                    },
                ],
                "ParserQuery": (
                    "source | project TimeGenerated, EventUid"
                ),
            },
            "Contoso_CL",
            [TIMESTAMP_1],
        )

        self.assertIn(
            "let Contoso_CL = materialize(table('Contoso_CL')",
            query,
        )
        self.assertIn("disabled=false", query)
        self.assertIn("pack=true", query)
        self.assertIn(f"datetime({TIMESTAMP_1})", query)

    def test_qtp_query_omits_unsupported_pack_parameter(self):
        query = VALIDATION.build_query_time_parser_query(
            {
                "ParserParams": [
                    {
                        "Name": "disabled",
                        "Type": "bool",
                        "Default": False,
                    }
                ],
                "ParserQuery": (
                    "source | project TimeGenerated, EventUid"
                ),
            },
            "Contoso_CL",
            [TIMESTAMP_1],
        )

        self.assertIn("disabled=false", query)
        self.assertNotIn("pack=true", query)

    def test_qtp_query_rejects_non_boolean_pack_parameter(self):
        with self.assertRaisesRegex(
            VALIDATION.ValidationError,
            "pack parameter must be boolean",
        ):
            VALIDATION.build_query_time_parser_query(
                {
                    "ParserParams": [
                        {
                            "Name": "pack",
                            "Type": "string",
                            "Default": "false",
                        }
                    ],
                    "ParserQuery": (
                        "source | project TimeGenerated"
                    ),
                },
                "Contoso_CL",
                [TIMESTAMP_1],
            )


class FilterValidationTests(unittest.TestCase):
    def snapshot(self):
        return {
            "timestampValues": [TIMESTAMP_1, TIMESTAMP_2],
            "rows": [
                {"TimeGenerated": TIMESTAMP_1, "EventType": "Login"},
                {"TimeGenerated": TIMESTAMP_1, "EventType": "Logout"},
                {"TimeGenerated": TIMESTAMP_2, "EventType": "Logout"},
            ],
        }

    def validator(self):
        return VALIDATION.AsimIngestionValidator(
            Path(__file__).resolve().parents[4]
        )

    def test_selective_filter_reports_selected_and_rejected_rows(self):
        client = FakeQueryClient(
            [
                (
                    "filter",
                    query_table(
                        [
                            ("TimeGenerated", "datetime"),
                            ("_AsimSelectedCount", "long"),
                        ],
                        [
                            {
                                "TimeGenerated": TIMESTAMP_1,
                                "_AsimSelectedCount": 1,
                            }
                        ],
                    ),
                )
            ]
        )

        result = self.validator().evaluate_filter(
            client,
            self.snapshot(),
            {
                "SourceRawTable": "Contoso_CL",
                "ParserFilterQuery": (
                    "source | where EventType == 'Login'"
                ),
            },
        )

        self.assertEqual("selective", result["mode"])
        self.assertEqual(1, result["selectedRowCount"])
        self.assertEqual(2, result["rejectedRowCount"])
        self.assertEqual(
            {TIMESTAMP_1: 1, TIMESTAMP_2: 0},
            result["selectedCountsByTimestamp"],
        )

    def test_selective_filter_requires_rejected_fixture_row(self):
        client = FakeQueryClient(
            [
                (
                    "filter",
                    query_table(
                        [
                            ("TimeGenerated", "datetime"),
                            ("_AsimSelectedCount", "long"),
                        ],
                        [
                            {
                                "TimeGenerated": TIMESTAMP_1,
                                "_AsimSelectedCount": 2,
                            },
                            {
                                "TimeGenerated": TIMESTAMP_2,
                                "_AsimSelectedCount": 1,
                            },
                        ],
                    ),
                )
            ]
        )

        with self.assertRaisesRegex(
            VALIDATION.ValidationError, "at least one rejected"
        ):
            self.validator().evaluate_filter(
                client,
                self.snapshot(),
                {
                    "SourceRawTable": "Contoso_CL",
                    "ParserFilterQuery": (
                        "source | where EventType != 'Never'"
                    ),
                },
            )

    def test_filter_requires_at_least_one_selected_row(self):
        client = FakeQueryClient(
            [
                (
                    "filter",
                    query_table(
                        [
                            ("TimeGenerated", "datetime"),
                            ("_AsimSelectedCount", "long"),
                        ],
                        [],
                    ),
                )
            ]
        )

        with self.assertRaisesRegex(
            VALIDATION.ValidationError, "at least one fixture row"
        ):
            self.validator().evaluate_filter(
                client,
                self.snapshot(),
                {
                    "SourceRawTable": "Contoso_CL",
                    "ParserFilterQuery": (
                        "source | where EventType == 'Never'"
                    ),
                },
            )

    def test_source_passthrough_allows_zero_rejected_rows(self):
        client = FakeQueryClient(
            [
                (
                    "filter",
                    query_table(
                        [
                            ("TimeGenerated", "datetime"),
                            ("_AsimSelectedCount", "long"),
                        ],
                        [
                            {
                                "TimeGenerated": TIMESTAMP_1,
                                "_AsimSelectedCount": 2,
                            },
                            {
                                "TimeGenerated": TIMESTAMP_2,
                                "_AsimSelectedCount": 1,
                            },
                        ],
                    ),
                )
            ]
        )

        result = self.validator().evaluate_filter(
            client,
            self.snapshot(),
            {
                "SourceRawTable": "Contoso_CL",
                "ParserFilterQuery": "source",
            },
        )

        self.assertEqual("pass-through", result["mode"])
        self.assertEqual(0, result["rejectedRowCount"])

    def test_source_passthrough_allows_scalar_let_prerequisite(self):
        client = FakeQueryClient(
            [
                (
                    "filter",
                    query_table(
                        [
                            ("TimeGenerated", "datetime"),
                            ("_AsimSelectedCount", "long"),
                        ],
                        [
                            {
                                "TimeGenerated": TIMESTAMP_1,
                                "_AsimSelectedCount": 2,
                            },
                            {
                                "TimeGenerated": TIMESTAMP_2,
                                "_AsimSelectedCount": 1,
                            },
                        ],
                    ),
                )
            ]
        )

        result = self.validator().evaluate_filter(
            client,
            self.snapshot(),
            {
                "SourceRawTable": "Contoso_CL",
                "ParserFilterQuery": (
                    "let accepted = true;\nsource"
                ),
            },
        )

        self.assertEqual("pass-through", result["mode"])


class ParityTests(unittest.TestCase):
    def schema(self):
        return [
            {"name": "TimeGenerated", "type": "datetime"},
            {"name": "EventUid", "type": "string"},
            {"name": "Payload", "type": "dynamic"},
            {"name": "Enabled", "type": "boolean"},
            {"name": "Message", "type": "string"},
        ]

    def test_parity_ignores_row_and_dynamic_object_key_order(self):
        expected_rows = [
            {
                "TimeGenerated": TIMESTAMP_1,
                "EventUid": "event-1",
                "Payload": {"b": 2, "a": 1},
                "Enabled": False,
                "Message": "",
            },
            {
                "TimeGenerated": TIMESTAMP_1,
                "EventUid": "event-1",
                "Payload": {"b": 2, "a": 1},
                "Enabled": False,
                "Message": "",
            },
            {
                "TimeGenerated": TIMESTAMP_2,
                "EventUid": "event-2",
                "Payload": [],
                "Enabled": True,
                "Message": "value",
            },
        ]
        actual_rows = [
            {
                "TimeGenerated": TIMESTAMP_2,
                "EventUid": "event-2",
                "Payload": "[]",
                "Enabled": True,
                "Message": "value",
            },
            {
                "TimeGenerated": TIMESTAMP_1,
                "EventUid": "event-1",
                "Payload": '{"a":1,"b":2}',
                "Enabled": False,
                "Message": "",
            },
            {
                "TimeGenerated": TIMESTAMP_1,
                "EventUid": "event-1",
                "Payload": '{"b":2,"a":1}',
                "Enabled": False,
                "Message": "",
            },
        ]

        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=expected_rows,
            actual_schema=self.schema(),
            actual_rows=actual_rows,
        )

        self.assertEqual("passed", result["status"])

    def test_parity_preserves_duplicate_multiplicity(self):
        row = {
            "TimeGenerated": TIMESTAMP_1,
            "EventUid": "event-1",
            "Payload": {},
            "Enabled": False,
            "Message": "",
        }

        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=[row, row],
            actual_schema=self.schema(),
            actual_rows=[row],
        )

        self.assertEqual("failed", result["status"])
        self.assertEqual(1, result["rows"]["missingRowCount"])
        self.assertEqual(
            1, len(result["rows"]["duplicateCountDifferences"])
        )

    def test_parity_distinguishes_null_and_empty_string(self):
        expected = {
            "TimeGenerated": TIMESTAMP_1,
            "EventUid": "event-1",
            "Payload": {},
            "Enabled": False,
            "Message": None,
        }
        actual = dict(expected, Message="")

        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=[expected],
            actual_schema=self.schema(),
            actual_rows=[actual],
        )

        self.assertEqual("failed", result["status"])

    def test_parity_preserves_dynamic_array_order(self):
        expected = {
            "TimeGenerated": TIMESTAMP_1,
            "EventUid": "event-1",
            "Payload": [1, 2],
            "Enabled": False,
            "Message": "",
        }
        actual = dict(expected, Payload=[2, 1])

        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=[expected],
            actual_schema=self.schema(),
            actual_rows=[actual],
        )

        self.assertEqual("failed", result["status"])

    def test_parity_normalizes_equivalent_datetime_forms(self):
        expected = {
            "TimeGenerated": "2026-10-19T22:00:00.1234567+02:00",
            "EventUid": "event-1",
            "Payload": {},
            "Enabled": False,
            "Message": "",
        }
        actual = dict(expected, TimeGenerated=TIMESTAMP_1)

        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=[expected],
            actual_schema=self.schema(),
            actual_rows=[actual],
        )

        self.assertEqual("passed", result["status"])

    def test_parity_reports_schema_differences_before_rows(self):
        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=[],
            actual_schema=self.schema()[:-1],
            actual_rows=[],
        )

        self.assertEqual("failed", result["status"])
        self.assertEqual(
            ["Message"],
            result["schema"]["missingInIngestTime"],
        )
        self.assertIsNone(result["rows"])

    def test_parity_ignores_additional_ingest_time_columns(self):
        expected_schema = self.schema()
        actual_schema = [
            *self.schema(),
            {"name": "AdditionalNativeColumn", "type": "string"},
        ]
        expected_row = {
            "TimeGenerated": TIMESTAMP_1,
            "EventUid": "event-1",
            "Payload": {},
            "Enabled": False,
            "Message": "",
        }
        actual_row = {
            **expected_row,
            "AdditionalNativeColumn": "ignored",
        }

        result = VALIDATION.compare_parser_outputs(
            expected_schema=expected_schema,
            expected_rows=[expected_row],
            actual_schema=actual_schema,
            actual_rows=[actual_row],
        )

        self.assertEqual("passed", result["status"])
        self.assertEqual(
            ["AdditionalNativeColumn"],
            result["schema"]["ignoredAdditionalIngestTime"],
        )

    def test_parity_rejects_qtp_column_type_mismatch(self):
        actual_schema = [
            dict(column)
            for column in self.schema()
        ]
        next(
            column
            for column in actual_schema
            if column["name"] == "EventUid"
        )["type"] = "dynamic"

        result = VALIDATION.compare_parser_outputs(
            expected_schema=self.schema(),
            expected_rows=[],
            actual_schema=actual_schema,
            actual_rows=[],
        )

        self.assertEqual("failed", result["status"])
        self.assertEqual(
            "EventUid",
            result["schema"]["typeMismatches"][0]["column"],
        )


class OutputValidationTests(unittest.TestCase):
    def validator(self):
        return VALIDATION.AsimIngestionValidator(
            Path(__file__).resolve().parents[4]
        )

    def parser_document(self):
        return {
            "Normalization": {"Schema": "Authentication"},
            "SourceRawTable": "Contoso_CL",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": (
                "source\n"
                "| project TimeGenerated, EventUid, EventVendor"
            ),
        }

    def source_snapshot(self):
        return {
            "timestampValues": [TIMESTAMP_1],
            "rows": [{"TimeGenerated": TIMESTAMP_1}],
        }

    def output_table(self):
        return query_table(
            [
                ("TimeGenerated", "datetime"),
                ("EventUid", "string"),
                ("EventVendor", "string"),
            ],
            [
                {
                    "TimeGenerated": TIMESTAMP_1,
                    "EventUid": "event-1",
                    "EventVendor": "Contoso",
                }
            ],
        )

    def empty_tester_result(self):
        return query_table([("Result", "string")], [])

    def test_runs_asim_tests_and_optional_parity(self):
        client = FakeQueryClient(
            [
                (
                    "asim-data",
                    query_table(
                        [("Result", "string")],
                        [{"Result": "(1) Warning: example"}],
                    ),
                ),
                ("qtp-execution", self.output_table()),
                ("target-output", self.output_table()),
            ]
        )
        qtp = {
            "ParserParams": [
                {
                    "Name": "disabled",
                    "Type": "bool",
                    "Default": False,
                },
                {
                    "Name": "pack",
                    "Type": "bool",
                    "Default": False,
                },
            ],
            "ParserQuery": (
                "Contoso_CL\n"
                "| project TimeGenerated, EventUid, EventVendor"
            ),
        }

        result = self.validator().validate_outputs(
            client,
            self.source_snapshot(),
            self.parser_document(),
            qtp,
        )

        self.assertEqual("passed", result["status"])
        self.assertEqual(
            "parser-dcr-output-stream",
            result["schemaValidation"]["authority"],
        )
        self.assertEqual("passed", result["dataTest"]["status"])
        self.assertEqual("passed", result["parity"]["status"])
        data_query = next(
            item["query"]
            for item in client.queries
            if item["stage"] == "asim-data"
        )
        self.assertIn("ASimAuthenticationEventLogs", data_query)
        self.assertIn(f"datetime({TIMESTAMP_1})", data_query)
        qtp_query = next(
            item["query"]
            for item in client.queries
            if item["stage"] == "qtp-execution"
        )
        self.assertIn("disabled=false", qtp_query)
        self.assertIn("pack=true", qtp_query)
        target_query = next(
            item["query"]
            for item in client.queries
            if item["stage"] == "target-output"
        )
        self.assertIn(
            "| project TimeGenerated, EventUid, EventVendor",
            target_query,
        )

    def test_without_qtp_reports_parity_not_applicable(self):
        client = FakeQueryClient(
            [
                ("asim-data", self.empty_tester_result()),
            ]
        )

        result = self.validator().validate_outputs(
            client,
            self.source_snapshot(),
            self.parser_document(),
            None,
        )

        self.assertEqual(
            "not-applicable", result["parity"]["status"]
        )

    def test_asim_data_error_fails_required_validation(self):
        client = FakeQueryClient(
            [
                (
                    "asim-data",
                    query_table(
                        [("Result", "string")],
                        [{"Result": "(0) Error: invalid value"}],
                    ),
                ),
            ]
        )

        with self.assertRaisesRegex(
            VALIDATION.ValidationError,
            "ASimDataTester reported errors",
        ):
            self.validator().validate_outputs(
                client,
                self.source_snapshot(),
                self.parser_document(),
                None,
            )


if __name__ == "__main__":
    unittest.main()
