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
    def test_dns_data_tester_normalizes_physical_threat_columns(self):
        query = VALIDATION.build_asim_tester_query(
            tester_name="ASimDataTester",
            tester_query="T | project Result = 'test'",
            target_table="ASimDnsActivityLogs",
            timestamps=[TIMESTAMP_1],
            schema_name="Dns",
        )

        target_query, tester_query = query.split(
            "let _AsimValidationTester", 1
        )
        self.assertIn(f"datetime({TIMESTAMP_1})", target_query)
        for field in (
            "ThreatFirstReportedTime",
            "ThreatLastReportedTime",
        ):
            self.assertIn(
                f'{field} = coalesce(column_ifexists("{field}_d", '
                f'datetime(null)), todatetime(column_ifexists('
                f'"{field}", "")))',
                target_query,
            )
        self.assertIn(
            'ThreatOriginalRiskLevel = coalesce(column_ifexists('
            '"ThreatOriginalRiskLevel_s", ""), tostring(column_ifexists('
            '"ThreatOriginalRiskLevel", int(null))))',
            target_query,
        )
        self.assertIn(
            "| invoke _AsimValidationTester('Dns')", tester_query
        )

    def test_data_tester_leaves_other_target_tables_unchanged(self):
        for table, schema in (
            ("ASimAuthenticationEventLogs", "Authentication"),
            ("CustomDns_CL", "Dns"),
        ):
            with self.subTest(table=table):
                query = VALIDATION.build_asim_tester_query(
                    tester_name="ASimDataTester",
                    tester_query="T | project Result = 'test'",
                    target_table=table,
                    timestamps=[TIMESTAMP_1],
                    schema_name=schema,
                )

                self.assertIn(
                    f"{table}\n| where TimeGenerated in "
                    f"(datetime({TIMESTAMP_1})));",
                    query,
                )
                self.assertNotIn("ThreatFirstReportedTime", query)
                self.assertNotIn("ThreatLastReportedTime", query)
                self.assertNotIn("ThreatOriginalRiskLevel", query)

    def test_builds_typed_fixture_filter_query(self):
        query = VALIDATION.build_filter_count_query(
            "source",
            source_schema=[
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Message", "type": "string"},
                {"name": "Enabled", "type": "boolean"},
                {"name": "Count", "type": "long"},
                {"name": "Score", "type": "real"},
                {"name": "Payload", "type": "dynamic"},
                {"name": "CorrelationId", "type": "guid"},
                {"name": "Column Name", "type": "string"},
                {"name": "NullableString", "type": "string"},
            ],
            source_rows=[
                {
                    "TimeGenerated": TIMESTAMP_1,
                    "Message": r"C:\logs\//keep 'quoted'",
                    "Enabled": True,
                    "Count": None,
                    "Score": 1.5,
                    "Payload": {"a": [1, True]},
                    "CorrelationId": (
                        "00000000-0000-0000-0000-000000000001"
                    ),
                    "Column Name": "quoted",
                    "NullableString": None,
                }
            ],
        )

        self.assertIn(
            "datatable(TimeGenerated:datetime, Message:string, "
            "Enabled:bool, Count:long, Score:real, "
            "Payload:dynamic, CorrelationId:guid, "
            "['Column Name']:string, NullableString:string)",
            query,
        )
        self.assertIn(
            r"@'C:\logs\//keep ''quoted'''",
            query,
        )
        self.assertIn("true, long(null), 1.5", query)
        self.assertNotIn("string(null)", query)
        self.assertTrue(query.count("@''") >= 1)
        self.assertIn('dynamic({"a":[1,true]})', query)
        self.assertIn(
            "guid(00000000-0000-0000-0000-000000000001)",
            query,
        )
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
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "EventType", "type": "string"},
            ],
            "rows": [
                {"TimeGenerated": TIMESTAMP_1, "EventType": "Login"},
                {"TimeGenerated": TIMESTAMP_1, "EventType": "Logout"},
                {"TimeGenerated": TIMESTAMP_2, "EventType": "Logout"},
            ],
        }

    def validator(self):
        return VALIDATION.AsimIngestionValidator(
            Path(__file__).resolve().parents[5]
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
        filter_query = client.queries[0]["query"]
        self.assertIn(
            "datatable(TimeGenerated:datetime, EventType:string)",
            filter_query,
        )
        self.assertNotIn("materialize(Contoso_CL", filter_query)

    def test_filter_counts_canonicalize_trailing_zero_timestamp(self):
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
                                "TimeGenerated":
                                    "2026-10-19T20:00:00.123456Z",
                                "_AsimSelectedCount": 1,
                            }
                        ],
                    ),
                )
            ]
        )
        snapshot = {
            "timestampValues": [
                "2026-10-19T20:00:00.1234560Z"
            ],
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            "rows": [
                {
                    "TimeGenerated":
                        "2026-10-19T20:00:00.1234560Z"
                }
            ],
        }

        result = self.validator().evaluate_filter(
            client,
            snapshot,
            {
                "SourceRawTable": "Contoso_CL",
                "ParserFilterQuery": "source",
            },
        )

        self.assertEqual(
            {"2026-10-19T20:00:00.1234560Z": 1},
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
            Path(__file__).resolve().parents[5]
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

    def qtp_output_table(self, *, event_vendor="Contoso"):
        return query_table(
            [
                ("TimeGenerated", "datetime"),
                ("EventUid", "string"),
                ("EventVendor", "string"),
                ("EventSchema", "string"),
                ("QtpOnly", "string"),
                ("DifferentType", "string"),
                ("Type", "string"),
            ],
            [
                {
                    "TimeGenerated": TIMESTAMP_1,
                    "EventUid": "event-1",
                    "EventVendor": event_vendor,
                    "EventSchema": "Authentication",
                    "QtpOnly": "qtp",
                    "DifferentType": "1",
                    "Type": "Contoso_CL",
                }
            ],
        )

    def itp_output_table(
        self,
        *,
        event_vendor="Contoso",
        different_type="string",
    ):
        different_value = "1" if different_type == "string" else 1
        return query_table(
            [
                ("TimeGenerated", "datetime"),
                ("EventUid", "string"),
                ("EventVendor", "string"),
                ("ItpOnly", "string"),
                ("DifferentType", different_type),
                ("Type", "string"),
            ],
            [
                {
                    "TimeGenerated": TIMESTAMP_1,
                    "EventUid": "event-1",
                    "EventVendor": event_vendor,
                    "ItpOnly": "itp",
                    "DifferentType": different_value,
                    "Type": "ASimAuthenticationEventLogs",
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
                ("qtp-execution", self.qtp_output_table()),
                ("target-output", self.itp_output_table()),
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
        self.assertEqual(
            1,
            sum(
                item["stage"] == "asim-data"
                for item in client.queries
            ),
        )
        self.assertEqual(
            [
                "TimeGenerated",
                "EventUid",
                "EventVendor",
                "DifferentType",
            ],
            [
                column["name"]
                for column in result["intersect_schema"]
            ],
        )
        self.assertEqual(
            [
                {
                    "TimeGenerated": TIMESTAMP_1,
                    "EventUid": "event-1",
                    "EventVendor": "Contoso",
                    "DifferentType": "1",
                }
            ],
            result["qtp_rows_filtered"],
        )
        self.assertEqual(
            result["qtp_rows_filtered"],
            result["itp_rows_filtered"],
        )
        self.assertTrue(
            all(
                column["typeConsistent"]
                for column in result["intersect_schema"]
            )
        )
        self.assertIn("EventSchema", result["qtp_rows"][0])
        self.assertNotIn("EventSchema", result["itp_rows"][0])
        self.assertIn("ItpOnly", result["itp_rows"][0])
        self.assertEqual(
            "Contoso_CL", result["qtp_rows"][0]["Type"]
        )
        self.assertEqual(
            "ASimAuthenticationEventLogs",
            result["itp_rows"][0]["Type"],
        )
        self.assertNotIn(
            "Type",
            {
                column["name"]
                for column in result["intersect_schema"]
            },
        )
        self.assertNotIn("Type", result["qtp_rows_filtered"][0])
        self.assertNotIn("Type", result["itp_rows_filtered"][0])
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
        self.assertNotIn("| project", target_query)

    def test_parity_failure_returns_full_and_filtered_artifacts(self):
        client = FakeQueryClient(
            [
                ("asim-data", self.empty_tester_result()),
                ("qtp-execution", self.qtp_output_table()),
                (
                    "target-output",
                    self.itp_output_table(event_vendor="Different"),
                ),
            ]
        )
        qtp = {
            "ParserParams": [],
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

        self.assertEqual("failed", result["status"])
        self.assertEqual("parity", result["failure"]["stage"])
        self.assertEqual("failed", result["parity"]["status"])
        self.assertTrue(result["qtp_schema"])
        self.assertTrue(result["qtp_rows"])
        self.assertTrue(result["itp_schema"])
        self.assertTrue(result["itp_rows"])
        self.assertTrue(result["intersect_schema"])
        self.assertTrue(result["qtp_rows_filtered"])
        self.assertTrue(result["itp_rows_filtered"])

    def test_shared_column_type_mismatch_fails_schema_parity(self):
        client = FakeQueryClient(
            [
                ("asim-data", self.empty_tester_result()),
                ("qtp-execution", self.qtp_output_table()),
                (
                    "target-output",
                    self.itp_output_table(different_type="long"),
                ),
            ]
        )
        qtp = {
            "ParserParams": [],
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

        self.assertEqual("failed", result["status"])
        mismatch = next(
            column
            for column in result["intersect_schema"]
            if column["name"] == "DifferentType"
        )
        self.assertEqual("string", mismatch["qtpType"])
        self.assertEqual("long", mismatch["itpType"])
        self.assertFalse(mismatch["typeConsistent"])
        self.assertEqual("failed", result["parity"]["status"])
        self.assertEqual(
            [
                {
                    "column": "DifferentType",
                    "queryTimeType": "string",
                    "ingestTimeType": "long",
                }
            ],
            result["parity"]["schema"]["typeMismatches"],
        )
        self.assertIsNone(result["parity"]["rows"])

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
